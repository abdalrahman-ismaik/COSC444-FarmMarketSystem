"""LangChain + Gemini natural-language assistant (READ-ONLY).

Safety layers:
 1. The prompt asks for one SELECT only, or CLARIFY / NOT_ANSWERABLE.
 2. validate_sql() rejects anything that is not a single, plain SELECT on approved tables.
 3. The query runs inside a READ ONLY transaction (the database itself refuses writes).
 4. Results are capped at 200 rows. Errors are replaced by friendly messages.
"""
import os
import re

import db

ALLOWED_TABLES = {
    "v_lot_stock", "v_request_status", "farms", "markets", "emirates", "crops", "units",
    "crop_cycles", "harvest_lots", "stock_movements", "market_requests", "allocations",
    "delivery_receipts", "request_status_history", "farm_users", "users",
}
BLOCKED_WORDS = [
    "insert", "update", "delete", "drop", "alter", "truncate", "create", "replace", "rename",
    "grant", "revoke", "call", "execute", "prepare", "handler", "lock", "unlock", "set",
    "load_file", "outfile", "dumpfile", "sleep", "benchmark", "image_data", "information_schema",
    "mysql", "performance_schema", "sys", "into",
]
MAX_ROWS = 200

PROMPT = """You are a careful MySQL assistant for a farm-to-market food availability database.
Write exactly ONE read-only MySQL SELECT query that answers the user's question.

Rules:
- Output only the SQL, with no explanation.
- Only SELECT. Never write INSERT, UPDATE, DELETE, DROP, ALTER or any other statement.
- Use only the tables, views and columns listed below.
- Prefer the view v_lot_stock for stock questions (columns on_hand, reserved, available)
  and v_request_status for market request questions.
- Expected quantities in crop_cycles are forecasts, NOT stock. Never add them to available stock.
- Never add or compare quantities that have different unit_code values; group by unit_code.
- Preserve every explicit filter in the question: crop, farm, market, emirate, status and date.
  Apply these filters BEFORE aggregation. Never substitute all-produce totals for one crop.
  'Dates' is a crop name (crop_name = 'Dates'), not a request for a date column.
  Example: Dates available by unit is
  SELECT unit_code, SUM(available) AS available FROM v_lot_stock
  WHERE crop_name = 'Dates' GROUP BY unit_code
- Today's date is CURDATE().
- Credentials are not available to this assistant. Product image BLOBs exist in the application
  database but are deliberately excluded from your allowed schema and must never be returned.
  Refuse requests for credentials or image bytes without claiming that stored images do not exist.
- If the question is ambiguous (for example it does not say which crop, farm or market and that matters),
  output exactly: CLARIFY: <one short question back to the user>
- If the question cannot be answered from this schema, or asks to change data, output exactly:
  NOT_ANSWERABLE: <short reason>

Database schema:
{schema}

User question:
{question}
"""

SUMMARY_PROMPT = """You are a helpful assistant for farmers and market buyers.
Answer the user's question in 1-3 short, plain-English sentences using ONLY the SQL result below.
Always include units (kg, box ...). If the result is empty, say that no matching records were found.

Question: {question}
Columns: {columns}
Rows: {rows}
"""


class AssistantError(Exception):
    pass


def validate_sql(sql):
    """Return a safe, limited SQL string or raise AssistantError."""
    s = (sql or "").strip().rstrip(";").strip()
    low = s.lower()
    if not low:
        raise AssistantError("The assistant did not produce a query.")
    if ";" in s or "--" in s or "/*" in s or "#" in s:
        raise AssistantError("Only one simple query is allowed.")
    if not (low.startswith("select") or low.startswith("with")):
        raise AssistantError("Only read-only SELECT questions are allowed.")
    for word in BLOCKED_WORDS:
        if re.search(rf"\b{word}\b", low):
            raise AssistantError("This request is not allowed. The assistant can only read data.")
    cte_names = set(re.findall(r"\b(\w+)\s+as\s*\(", low))
    for name in re.findall(r"\b(?:from|join)\s+`?(\w+)`?", low):
        if name not in ALLOWED_TABLES and name not in cte_names:
            raise AssistantError(f"The assistant cannot use '{name}'.")
    return f"SELECT * FROM ({s}) AS assistant_result LIMIT {MAX_ROWS}"


def extract_sql(text):
    text = (text or "").strip()
    block = re.search(r"```(?:sql)?\s*(.*?)```", text, re.IGNORECASE | re.DOTALL)
    return (block.group(1) if block else text).strip()


def schema_text():
    marks = ",".join(["%s"] * len(ALLOWED_TABLES))
    rows = db.query(f"""SELECT TABLE_NAME, COLUMN_NAME, DATA_TYPE, COLUMN_TYPE FROM INFORMATION_SCHEMA.COLUMNS
                        WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME IN ({marks})
                        AND DATA_TYPE NOT LIKE '%%blob%%'
                        ORDER BY TABLE_NAME, ORDINAL_POSITION""", list(ALLOWED_TABLES))
    tables = {}
    for r in rows:
        col_type = r["COLUMN_TYPE"] if r["DATA_TYPE"] == "enum" else r["DATA_TYPE"]
        tables.setdefault(r["TABLE_NAME"], []).append(f"{r['COLUMN_NAME']} ({col_type})")
    return "\n".join(f"{t}: " + ", ".join(cols) for t, cols in tables.items())


def run_readonly(sql):
    conn = db.get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("START TRANSACTION READ ONLY")
            cur.execute(sql)
            rows = cur.fetchall()
            columns = [d[0] for d in cur.description] if cur.description else []
        return columns, rows
    finally:
        conn.rollback()
        conn.close()


class Assistant:
    def __init__(self, llm=None):
        self._llm = llm
        self._schema = None

    @staticmethod
    def has_key():
        key = os.getenv("GEMINI_API_KEY", "").strip()
        return bool(key) and key != "YOUR_API_KEY"

    def _model(self):
        if self._llm is None:
            if not self.has_key():
                raise AssistantError("The AI assistant needs a Gemini API key. Add GEMINI_API_KEY to the .env file.")
            from langchain_google_genai import ChatGoogleGenerativeAI
            self._llm = ChatGoogleGenerativeAI(
                model=os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite"),
                google_api_key=os.getenv("GEMINI_API_KEY"), temperature=0,
                timeout=30, max_retries=1)
        return self._llm

    def _chain(self, template):
        from langchain_core.prompts import ChatPromptTemplate
        from langchain_core.output_parsers import StrOutputParser
        return ChatPromptTemplate.from_template(template) | self._model() | StrOutputParser()

    def ask(self, question):
        """Return a dict: kind ('answer'|'clarify'|'not_answerable'|'error'), text, sql, columns, rows."""
        question = (question or "").strip()
        if not question:
            return {"kind": "error", "text": "Please type a question."}
        if len(question) > 500:
            return {"kind": "error", "text": "Please keep your question under 500 characters."}
        try:
            if self._schema is None:
                self._schema = schema_text()
            raw = self._chain(PROMPT).invoke({"schema": self._schema, "question": question})
            out = extract_sql(raw)
            if out.upper().startswith("CLARIFY"):
                return {"kind": "clarify", "text": out.split(":", 1)[-1].strip() or "Could you be more specific?"}
            if out.upper().startswith("NOT_ANSWERABLE"):
                reason = out.split(":", 1)[-1].strip()
                return {"kind": "not_answerable",
                        "text": "I can't answer that from the farm and market records." + (f" ({reason})" if reason else "")}
            safe_sql = validate_sql(out)
            columns, rows = run_readonly(safe_sql)
            summary = self._chain(SUMMARY_PROMPT).invoke(
                {"question": question, "columns": columns, "rows": [list(r.values()) for r in rows[:50]]})
            return {"kind": "answer", "text": summary.strip(), "sql": out, "columns": columns, "rows": rows}
        except AssistantError as e:
            return {"kind": "error", "text": str(e)}
        except db.pymysql.err.MySQLError as e:
            code = e.args[0] if e.args else None
            if code in (1045, 1049, 2003, 2006, 2013):
                return {"kind": "error", "text": db.friendly_error(e)}
            return {"kind": "error", "text": "I couldn't run a query for that question. Try rephrasing it."}
        except Exception:
            return {"kind": "error", "text": "The AI service is not reachable right now. "
                                             "Check your internet connection and API key, then try again."}

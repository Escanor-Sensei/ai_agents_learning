"""
Tool: Database Query
Responsibility: Run READ-ONLY SQL queries against SQL Server (PaymentDB).

.NET analogy:
  pyodbc.connect()  ≈  new SqlConnection(connectionString)
  cursor.execute()  ≈  SqlCommand.ExecuteReader()
  cursor.fetchall() ≈  reader.Read() loop into a List<T>

Security rules (same as production .NET APIs):
  - SELECT only — no INSERT/UPDATE/DELETE/DROP allowed
  - Connection string loaded from .env — never hardcoded
  - Parameterized queries used where inputs are involved
"""

import os
import pyodbc
from dotenv import load_dotenv
from langchain_core.tools import tool

load_dotenv()

_CONNECTION_STRING = os.getenv("DB_CONNECTION_STRING")


def _is_safe_query(sql: str) -> bool:
    """Allow only SELECT statements — block any write or DDL operations."""
    normalized = sql.strip().upper()
    blocked = ["INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "TRUNCATE", "EXEC", "EXECUTE"]
    if not normalized.startswith("SELECT"):
        return False
    return not any(keyword in normalized for keyword in blocked)


@tool
def db_query(sql: str) -> str:
    """
    Executes a READ-ONLY SQL SELECT query against the PaymentDB SQL Server database
    and returns the results as a formatted string.
    Use this tool when the user asks about payment data, transactions, records,
    or anything that requires querying the database.
    Input must be a valid SQL SELECT statement only.
    Do NOT use INSERT, UPDATE, DELETE, or DROP — only SELECT is allowed.
    Example input: 'SELECT TOP 5 * FROM Payments ORDER BY CreatedAt DESC'
    """
    if not _CONNECTION_STRING:
        return "Database error: DB_CONNECTION_STRING is not set in environment."

    if not _is_safe_query(sql):
        return "Query rejected: only SELECT statements are permitted."

    try:
        # autocommit=True — read-only, no transaction needed
        with pyodbc.connect(_CONNECTION_STRING, autocommit=True) as conn:
            cursor = conn.cursor()
            cursor.execute(sql)

            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()

        if not rows:
            return "Query executed successfully but returned no rows."

        # Format as a readable table — like serializing a List<T> to string
        header = " | ".join(columns)
        separator = "-" * len(header)
        result_rows = [" | ".join(str(val) for val in row) for row in rows]

        return "\n".join([header, separator] + result_rows)

    except pyodbc.Error as e:
        return f"Database error: {e}"

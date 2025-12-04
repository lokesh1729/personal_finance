# server.py
from mcp.server.fastmcp import FastMCP
import psycopg2
from psycopg2.extras import RealDictCursor
import json

# Initialize the MCP Server
mcp = FastMCP("postgres-agent")

# Database Connection Config (In production, use env vars)
DB_CONFIG = {
    "dbname": "personal_finance",
    "user": "personal_finance",
    "password": "Lokramya#123",
    "host": "localhost",
    "port": "5432",
}


def get_connection():
    return psycopg2.connect(**DB_CONFIG)


@mcp.tool()
def get_schema() -> str:
    """
    Retrieves the list of tables and their columns from the database.
    Useful for understanding what data is available before querying.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT table_name, column_name, data_type 
        FROM information_schema.columns 
        WHERE table_schema = 'public' 
        ORDER BY table_name, ordinal_position;
    """
    )
    rows = cur.fetchall()
    conn.close()

    # Format as readable text for the LLM
    schema_summary = {}
    for table, col, dtype in rows:
        if table not in schema_summary:
            schema_summary[table] = []
        schema_summary[table].append(f"{col} ({dtype})")

    return json.dumps(schema_summary, indent=2)


@mcp.tool()
def run_read_only_query(sql: str) -> str:
    """
    Executes a SELECT SQL query and returns the results.
    Only SELECT statements are allowed for safety.
    """
    if not sql.strip().upper().startswith("SELECT"):
        return "Error: Only SELECT queries are allowed."

    try:
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute(sql)
        results = cur.fetchall()
        conn.close()
        return json.dumps(results, default=str)  # default=str handles dates/decimals
    except Exception as e:
        return f"Database Error: {str(e)}"


if __name__ == "__main__":
    mcp.run()

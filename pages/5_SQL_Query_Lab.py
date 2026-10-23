import re
import sqlite3
from pathlib import Path

import pandas as pd
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DB_PATH = PROJECT_ROOT / "data" / "cricbuzz.db"
QUERIES_PATH = PROJECT_ROOT / "sql" / "analytics_queries.sql"

st.set_page_config(
    page_title="SQL Query Lab | Cricbuzz LiveStats",
    page_icon="🧪",
    layout="wide",
)


def load_queries():
    """Read queries using their numbered SQL comment headings."""
    sql_text = QUERIES_PATH.read_text(encoding="utf-8-sig")

    headings = list(
        re.finditer(
            r"^\s*--\s*(\d+\.\s+[^\r\n]+)",
            sql_text,
            re.MULTILINE,
        )
    )

    query_items = []

    for index, heading in enumerate(headings):
        end = (
            headings[index + 1].start()
            if index + 1 < len(headings)
            else len(sql_text)
        )

        block = sql_text[heading.end():end]

        query_text = "\n".join(
            line
            for line in block.splitlines()
            if not line.lstrip().startswith("--")
        ).strip()

        if not re.match(
            r"^(SELECT|WITH)\b",
            query_text,
            re.IGNORECASE,
        ):
            continue

        title = heading.group(1).strip()
        difficulty_match = re.search(
            r"\[(Easy|Medium|Hard)\]",
            title,
            re.IGNORECASE,
        )

        difficulty = (
            difficulty_match.group(1).title()
            if difficulty_match
            else "Unspecified"
        )

        query_items.append(
            {
                "title": title,
                "difficulty": difficulty,
                "sql": query_text,
            }
        )

    return query_items


st.title("🧪 SQL Query Lab")
st.write(
    "Choose a saved analytics question, view its SQL, "
    "and run it against the local cricket database."
)
st.caption(
    "These queries analyze the demo records stored in SQLite. "
    "API dashboard data is fetched separately."
)

if not DB_PATH.exists():
    st.error(f"Database not found: {DB_PATH}")
    st.stop()

if not QUERIES_PATH.exists():
    st.error(f"SQL file not found: {QUERIES_PATH}")
    st.info("Put analytics_queries.sql inside the project's sql folder.")
    st.stop()

try:
    queries = load_queries()
except (OSError, UnicodeError) as error:
    st.error(f"Could not read the SQL file: {error}")
    st.stop()

if not queries:
    st.warning("No numbered SELECT or WITH queries were found.")
    st.stop()

st.success(f"Loaded {len(queries)} SQL queries.")

selected_difficulty = st.selectbox(
    "Difficulty",
    ["All", "Easy", "Medium", "Hard"],
)

filtered_queries = [
    item
    for item in queries
    if selected_difficulty == "All"
    or item["difficulty"] == selected_difficulty
]

if not filtered_queries:
    st.info("No questions were found for this difficulty.")
    st.stop()

selected_index = st.selectbox(
    "Choose a query",
    options=range(len(filtered_queries)),
    format_func=lambda index: filtered_queries[index]["title"],
)

selected_query = filtered_queries[selected_index]

st.subheader(selected_query["title"])
st.code(selected_query["sql"], language="sql")

if st.button("Run selected query", type="primary"):
    try:
        database_uri = DB_PATH.resolve().as_uri() + "?mode=ro"

        with sqlite3.connect(database_uri, uri=True) as connection:
            connection.execute("PRAGMA query_only = ON")

            result = pd.read_sql_query(
                selected_query["sql"],
                connection,
            )

        st.subheader("Query results")

        if result.empty:
            st.info("The query ran successfully but returned no rows.")
        else:
            st.dataframe(
                result,
                hide_index=True,
                width="stretch",
            )
            st.caption(f"Rows returned: {len(result)}")

    except Exception as error:
        st.error(f"The query could not run: {error}")
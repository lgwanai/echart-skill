from scripts.validate_agent_output import validate_text


def test_validate_agent_output_rejects_heredoc_direct_db_connection():
    text = """
    $ python3 << 'PYEOF'
    import psycopg2
    conn = psycopg2.connect('host=localhost dbname=china_mobile password=secret')
    PYEOF
    """

    errors = validate_text(text)

    assert any("HEREDOC_PYTHON" in error for error in errors)
    assert any("DIRECT_POSTGRES_CONNECT" in error for error in errors)
    assert any("DIRECT_POSTGRES_IMPORT" in error for error in errors)
    assert any("DIRECT_CONN_VARIABLE" in error for error in errors)


def test_validate_agent_output_accepts_sql_runner_file_flow():
    text = """
    cat queries/city_h1_yoy.sql
    python scripts/sql_runner.py --profile china_mobile --file queries/city_h1_yoy.sql --output json
    """

    assert validate_text(text) == []


def test_validate_agent_output_accepts_sql_file_write_then_runner():
    text = """
    cat > queries/city_h1_yoy.sql
    SELECT city_name, SUM(room_nights) FROM hotel_order GROUP BY 1;
    python scripts/sql_runner.py --profile china_mobile --file queries/city_h1_yoy.sql --output json
    """

    assert validate_text(text) == []


def test_validate_agent_output_accepts_wrapped_sql_runner_file_input():
    text = """
    python scripts/sql_runner.py --profile china_mobile \\
      --output json \\
      --file queries/city_h1_yoy.sql
    """

    assert validate_text(text) == []


def test_validate_agent_output_rejects_python_executor_for_sql_file():
    text = """
    import psycopg2
    conn = psycopg2.connect('host=localhost dbname=china_mobile password=secret')
    sql = open('queries/city_h1_yoy.sql').read()
    cur = conn.cursor()
    cur.execute(sql)
    """

    errors = validate_text(text)
    assert any("DIRECT_POSTGRES_IMPORT" in error for error in errors)
    assert any("DIRECT_CONN_VARIABLE" in error for error in errors)
    assert any("DIRECT_POSTGRES_CONNECT" in error for error in errors)
    assert any("DIRECT_CURSOR" in error for error in errors)
    assert any("DIRECT_CURSOR_EXECUTE" in error for error in errors)


def test_validate_agent_output_rejects_direct_duckdb_query_code():
    text = """
    import duckdb
    conn = duckdb.connect('workspace.duckdb')
    conn.execute('SELECT city_name, SUM(room_nights) FROM hotel_order GROUP BY 1').fetchall()
    """

    errors = validate_text(text)

    assert any("DIRECT_DUCKDB_CONNECT" in error for error in errors)
    assert any("DIRECT_CONN_VARIABLE" in error for error in errors)


def test_validate_agent_output_rejects_psycopg_v3_connection():
    text = """
    import psycopg
    connection = psycopg.connect('postgresql://localhost/china_mobile')
    cursor = connection.cursor()
    cursor.execute('SELECT 1')
    """

    errors = validate_text(text)

    assert any("DIRECT_POSTGRES_IMPORT" in error for error in errors)
    assert any("DIRECT_POSTGRES_CONNECT" in error for error in errors)
    assert any("DIRECT_CONN_VARIABLE" in error for error in errors)
    assert any("DIRECT_CURSOR" in error for error in errors)
    assert any("DIRECT_CURSOR_EXECUTE" in error for error in errors)


def test_validate_agent_output_accepts_sql_runner_sql_flow():
    text = """
    python scripts/metrics_manager.py effective
    python scripts/sql_runner.py --profile china_mobile --sql "SELECT city_name, SUM(room_nights) AS rn FROM hotel_order GROUP BY city_name" --output json
    """

    assert validate_text(text) == []


def test_validate_agent_output_accepts_direct_sql_runner_connection_args():
    text = """
    python scripts/sql_runner.py --type postgresql --host localhost --database china_mobile \
      --username china_mobile --password-env CHINA_MOBILE_PASSWORD \
      --sql "SELECT 1" --output json
    """

    assert validate_text(text) == []

import os
import pymysql
import pytest



DB_NAME = "RLMS_LAB4"
SHADOW_DB_NAME = "RLMS_LAB4_SHADOW"
HERE = os.path.dirname(os.path.abspath(__file__))
SCHEMA_FILE = os.path.join(HERE, "schema.sql")
SEED_FILE = os.path.join(HERE, "lab4_seed.sql")
SHADOW_SEED_FILE = os.path.join(HERE, "lab4_seed_shadow.sql")


@pytest.fixture(scope="session")
def admin_connection():
    conn = pymysql.connect(host="127.0.0.1", user="root", password="root", autocommit=True)
    yield conn
    conn.close()


@pytest.fixture(scope="session")
def public_connection():
    conn = pymysql.connect(host="127.0.0.1", user="root", password="root", database=DB_NAME, autocommit=True)
    yield conn
    conn.close()


@pytest.fixture(scope="session")
def shadow_connection():
    conn = pymysql.connect(host="127.0.0.1", user="root", password="root", database=SHADOW_DB_NAME, autocommit=True)
    yield conn
    conn.close()


def _load_sql_file_into_db(cur, path, required_for_msg):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Required file not found: {path}\n{required_for_msg}")
    with open(path, "r", encoding="utf-8") as f:
        sql_text = f.read()
    clean_lines = []
    for line in sql_text.split("\n"):
        if "--" in line:
            line = line.split("--")[0]
        clean_lines.append(line)
    sql_text = "\n".join(clean_lines)
    for statement in sql_text.split(";"):
        statement = statement.strip()
        if not statement or statement.upper().startswith("USE "):
            continue
        cur.execute(statement)


@pytest.fixture(scope="session", autouse=True)
def setup_database(admin_connection):
    """Runs once per test session: builds TWO independent databases, each
    freshly seeded with CURDATE()-relative data."""
    cur = admin_connection.cursor()
    for db_name, seed_file in ((DB_NAME, SEED_FILE), (SHADOW_DB_NAME, SHADOW_SEED_FILE)):
        cur.execute(f"DROP DATABASE IF EXISTS {db_name}")
        cur.execute(f"CREATE DATABASE {db_name}")
        cur.execute(f"USE {db_name}")
        _load_sql_file_into_db(cur, SCHEMA_FILE, "Lab 4 grading requires schema.sql to sit next to test_lab4.py.")
        _load_sql_file_into_db(cur, seed_file, "Lab 4 grading requires lab4_seed.sql and lab4_seed_shadow.sql to sit next to test_lab4.py.")
    cur.close()
    yield


@pytest.fixture
def cursor(public_connection, setup_database):
    cur = public_connection.cursor()
    yield cur
    cur.close()


@pytest.fixture
def shadow_cursor(shadow_connection, setup_database):
    cur = shadow_connection.cursor()
    yield cur
    cur.close()



def normalize(rows):
    return sorted(tuple(str(v) if v is not None else None for v in row) for row in rows)


def _is_effectively_blank(sql):
    stripped_lines = []
    for line in sql.split("\n"):
        if "--" in line:
            line = line.split("--")[0]
        stripped_lines.append(line)
    return "".join(stripped_lines).strip() == ""


def assert_matches_expected(cursor, shadow_cursor, sql, expected, shadow_expected, query_label):
    if expected is None or shadow_expected is None:
        pytest.skip(f"{query_label}: no expected-results entry filled in yet for one or both datasets -- skipping rather than risking a false pass.")

    assert not _is_effectively_blank(sql), (
        f"{query_label}: no SQL was written (only the placeholder comment "
        f"remains). Replace '-- WRITE YOUR SQL QUERY HERE' with an actual query."
    )

    cursor.execute(sql)
    actual_rows = normalize(cursor.fetchall())
    expected_rows = normalize(expected)

    shadow_cursor.execute(sql)
    shadow_actual_rows = normalize(shadow_cursor.fetchall())
    shadow_expected_rows = normalize(shadow_expected)

    public_ok = actual_rows == expected_rows
    shadow_ok = shadow_actual_rows == shadow_expected_rows

    if public_ok and shadow_ok:
        return

    details = []
    if not public_ok:
        details.append(
            f"public dataset result mismatch:\n"
            f"    Expected ({len(expected_rows)} row(s)): {expected_rows}\n"
            f"    Got      ({len(actual_rows)} row(s)): {actual_rows}"
        )
    if not shadow_ok:
        details.append(
            f"hidden verification dataset result mismatch: "
            f"expected {len(shadow_expected_rows)} row(s), "
            f"got {len(shadow_actual_rows)} row(s) "
        )
        if public_ok:
            details.append(
                "this query matched the public dataset but NOT the hidden one "
            )

    pytest.fail(f"{query_label} result mismatch:\n  " + "\n  ".join(details))


def assert_matches_expected_q16(cursor, shadow_cursor, sql, expected_offsets, shadow_expected_offsets, query_label):
    if expected_offsets is None or shadow_expected_offsets is None:
        pytest.skip(f"{query_label}: no expected-results entry filled in yet -- skipping.")

    assert not _is_effectively_blank(sql), (
        f"{query_label}: no SQL was written (only the placeholder comment "
        f"remains). Replace '-- WRITE YOUR SQL QUERY HERE' with an actual query."
    )

    def expand(cur, offsets):
        cur.execute("SELECT CURDATE()")
        today = cur.fetchone()[0]
        from datetime import timedelta
        return normalize([(pid, str(today + timedelta(days=int(off)))) for pid, off in offsets])

    cursor.execute(sql)
    actual_rows = normalize([(r[0], str(r[1])[:10]) for r in cursor.fetchall()])
    expected_rows = expand(cursor, expected_offsets)

    shadow_cursor.execute(sql)
    shadow_actual_rows = normalize([(r[0], str(r[1])[:10]) for r in shadow_cursor.fetchall()])
    shadow_expected_rows = expand(shadow_cursor, shadow_expected_offsets)

    public_ok = actual_rows == expected_rows
    shadow_ok = shadow_actual_rows == shadow_expected_rows

    if public_ok and shadow_ok:
        return

    details = []
    if not public_ok:
        details.append(
            f"public dataset result mismatch:\n"
            f"    Expected ({len(expected_rows)} row(s)): {expected_rows}\n"
            f"    Got      ({len(actual_rows)} row(s)): {actual_rows}"
        )
    if not shadow_ok:
        details.append(
            f"hidden verification dataset result mismatch: "
            f"expected {len(shadow_expected_rows)} row(s), "
            f"got {len(shadow_actual_rows)} row(s) (values withheld)"
        )
        if public_ok:
            details.append(
                " (this query matched the public dataset but NOT the hidden one)"
            )
    pytest.fail(f"{query_label} result mismatch:\n  " + "\n  ".join(details))




try:
    from lab4_answers import EXPECTED_RESULTS
except ImportError as exc:
    raise ImportError(
        "lab4_answers.py not found. This file holds the expected results"
    ) from exc

try:
    from lab4_answers_shadow import EXPECTED_RESULTS as SHADOW_EXPECTED_RESULTS
except ImportError as exc:
    raise ImportError(
        "lab4_answers_shadow.py not found. This file holds the private expected results "
    ) from exc


def test_01_query_1(cursor, shadow_cursor):
    """
    Query 1

    Select all persons ordered by FullName (Person has no separate
    first/last name columns).
    """
    sql = """
    SELECT PersonID, FullName FROM Person ORDER BY FullName
    """
    assert_matches_expected(cursor, shadow_cursor, sql, EXPECTED_RESULTS[1], SHADOW_EXPECTED_RESULTS[1], "Q1")

    # Order check: 
    cursor.execute(sql)
    rows = cursor.fetchall()
    assert rows, (
        "Q1: query returned zero rows  Person should never be empty in "
        "this seed; did you write the right query?"
    )
    names = [row[1] if len(row) > 1 else row[0] for row in rows]
    assert names == sorted(names), (
        f"Query 1 result is not sorted by FullName ascending.\n"
        f"  Got order: {names}\n"
        f"  Expected:  {sorted(names)}"
    )


def test_02_query_2(cursor, shadow_cursor):
    """
    Query 2

    List distinct research areas of laboratories.
    """
    sql = """
    SELECT DISTINCT ResearchArea FROM Laboratory
    """
    assert_matches_expected(cursor, shadow_cursor, sql, EXPECTED_RESULTS[2], SHADOW_EXPECTED_RESULTS[2], "Q2")


def test_03_query_3(cursor, shadow_cursor):
    """
    Query 3

    Retrieve research users who supervise at least one laboratory.
    """
    sql = """
    SELECT DISTINCT ru.PersonID FROM ResearchUser ru JOIN Laboratory l ON l.SupervisorID = ru.PersonID
    """
    assert_matches_expected(cursor, shadow_cursor, sql, EXPECTED_RESULTS[3], SHADOW_EXPECTED_RESULTS[3], "Q3")


def test_04_query_4(cursor, shadow_cursor):
    """
    Query 4

    Find all reservations scheduled within the next seven days.
    """
    sql = """
    SELECT ReservationID FROM Reservation WHERE PlannedStartTime >= CURDATE() AND PlannedStartTime < CURDATE() + INTERVAL 7 DAY
    """
    assert_matches_expected(cursor, shadow_cursor, sql, EXPECTED_RESULTS[4], SHADOW_EXPECTED_RESULTS[4], "Q4")


def test_05_query_5(cursor, shadow_cursor):
    """
    Query 5

    Count the number of reservations per laboratory.
    """
    sql = """
    SELECT eu.LabID, COUNT(*) FROM Reservation r JOIN EquipmentUnit eu ON r.SerialNumber = eu.SerialNumber GROUP BY eu.LabID
    """
    assert_matches_expected(cursor, shadow_cursor, sql, EXPECTED_RESULTS[5], SHADOW_EXPECTED_RESULTS[5], "Q5")


def test_06_query_6(cursor, shadow_cursor):
    """
    Query 6

    Compute the average purchase cost of equipment per laboratory (excluding any unit with a non-positive cost).
    """
    sql = """
    SELECT LabID, ROUND(AVG(PurchaseCost),2) FROM EquipmentUnit WHERE PurchaseCost > 0 GROUP BY LabID
    """
    assert_matches_expected(cursor, shadow_cursor, sql, EXPECTED_RESULTS[6], SHADOW_EXPECTED_RESULTS[6], "Q6")


def test_07_query_7(cursor, shadow_cursor):
    """
    Query 7

    List laboratories that contain more than ten equipment units.
    """
    sql = """
    SELECT LabID, COUNT(*) FROM EquipmentUnit GROUP BY LabID HAVING COUNT(*) > 10
    """
    assert_matches_expected(cursor, shadow_cursor, sql, EXPECTED_RESULTS[7], SHADOW_EXPECTED_RESULTS[7], "Q7")


def test_08_query_8(cursor, shadow_cursor):
    """
    Query 8

    Find all equipment belonging to the category 'Microscope' whose purchase cost is below 25000.
    """
    sql = """
    SELECT eu.SerialNumber FROM EquipmentUnit eu JOIN EquipmentModel em ON eu.ModelID = em.ModelID WHERE em.Category = 'Microscope' AND eu.PurchaseCost < 25000
    """
    assert_matches_expected(cursor, shadow_cursor, sql, EXPECTED_RESULTS[8], SHADOW_EXPECTED_RESULTS[8], "Q8")


def test_09_query_9(cursor, shadow_cursor):
    """
    Query 9

    For each laboratory, list the top three most expensive equipment items.
    """
    sql = """
    SELECT LabID, SerialNumber FROM (SELECT LabID, SerialNumber, PurchaseCost, ROW_NUMBER() OVER (PARTITION BY LabID ORDER BY PurchaseCost DESC) AS rn FROM EquipmentUnit) ranked WHERE rn <= 3
    """
    assert_matches_expected(cursor, shadow_cursor, sql, EXPECTED_RESULTS[9], SHADOW_EXPECTED_RESULTS[9], "Q9")


def test_10_query_10(cursor, shadow_cursor):
    """
    Query 10

    For each laboratory, return the number of reservations with status Approved, Pending, and Cancelled in a single result.
    """
    sql = """
    SELECT eu.LabID, SUM(CASE WHEN r.Status='Approved' THEN 1 ELSE 0 END), SUM(CASE WHEN r.Status='Pending' THEN 1 ELSE 0 END), SUM(CASE WHEN r.Status='Cancelled' THEN 1 ELSE 0 END) FROM Reservation r JOIN EquipmentUnit eu ON r.SerialNumber = eu.SerialNumber GROUP BY eu.LabID
    """
    assert_matches_expected(cursor, shadow_cursor, sql, EXPECTED_RESULTS[10], SHADOW_EXPECTED_RESULTS[10], "Q10")


def test_11_query_11(cursor, shadow_cursor):
    """
    Query 11

    List research users who have no reservation in the next thirty days.
    """
    sql = """
    SELECT ru.PersonID FROM ResearchUser ru WHERE ru.PersonID NOT IN (SELECT PersonID FROM Reservation WHERE PlannedStartTime >= CURDATE() AND PlannedStartTime < CURDATE() + INTERVAL 30 DAY)
    """
    assert_matches_expected(cursor, shadow_cursor, sql, EXPECTED_RESULTS[11], SHADOW_EXPECTED_RESULTS[11], "Q11")


def test_12_query_12(cursor, shadow_cursor):
    """
    Query 12

    For each research user, compute the total number of reservations and the percentage share of reservations in their laboratory (computed per lab they have reservations in).
    """
    sql = """
    SELECT ru.PersonID, eu.LabID, COUNT(*), ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM Reservation r2 JOIN EquipmentUnit eu2 ON r2.SerialNumber = eu2.SerialNumber WHERE eu2.LabID = eu.LabID),2) FROM Reservation r JOIN EquipmentUnit eu ON r.SerialNumber = eu.SerialNumber JOIN ResearchUser ru ON r.PersonID = ru.PersonID GROUP BY ru.PersonID, eu.LabID
    """
    assert_matches_expected(cursor, shadow_cursor, sql, EXPECTED_RESULTS[12], SHADOW_EXPECTED_RESULTS[12], "Q12")


def test_13_query_13(cursor, shadow_cursor):
    """
    Query 13

    Show all equipment units currently marked as UnderMaintenance and include the laboratory where each unit is located.
    """
    sql = """
    SELECT eu.SerialNumber, eu.LabID FROM EquipmentUnit eu WHERE eu.CurrentStatus = 'UnderMaintenance'
    """
    assert_matches_expected(cursor, shadow_cursor, sql, EXPECTED_RESULTS[13], SHADOW_EXPECTED_RESULTS[13], "Q13")


def test_14_query_14(cursor, shadow_cursor):
    """
    Query 14

    Find laboratories that contain every equipment category in the equipment catalog.
    """
    sql = """
    SELECT l.LabID FROM Laboratory l WHERE NOT EXISTS (SELECT em.Category FROM EquipmentModel em WHERE em.Category NOT IN (SELECT em2.Category FROM EquipmentUnit eu2 JOIN EquipmentModel em2 ON eu2.ModelID = em2.ModelID WHERE eu2.LabID = l.LabID))
    """
    assert_matches_expected(cursor, shadow_cursor, sql, EXPECTED_RESULTS[14], SHADOW_EXPECTED_RESULTS[14], "Q14")


def test_15_query_15(cursor, shadow_cursor):
    """
    Query 15

    For each laboratory and equipment category, return the average purchase cost and indicate whether it is above the overall average for that category.
    """
    sql = """
    SELECT eu.LabID, em.Category, CASE WHEN AVG(eu.PurchaseCost) > (SELECT AVG(eu2.PurchaseCost) FROM EquipmentUnit eu2 JOIN EquipmentModel em2 ON eu2.ModelID = em2.ModelID WHERE em2.Category = em.Category) THEN 'Above' ELSE 'Below or Equal' END FROM EquipmentUnit eu JOIN EquipmentModel em ON eu.ModelID = em.ModelID GROUP BY eu.LabID, em.Category
    """
    assert_matches_expected(cursor, shadow_cursor, sql, EXPECTED_RESULTS[15], SHADOW_EXPECTED_RESULTS[15], "Q15")


def test_16_query_16(cursor, shadow_cursor):
    """
    Query 16

    Return the next reservation date for each research user.
    """
    sql = """
    SELECT PersonID, MIN(PlannedStartTime) FROM Reservation WHERE PlannedStartTime >= CURDATE() GROUP BY PersonID
    """
    assert_matches_expected_q16(cursor, shadow_cursor, sql, EXPECTED_RESULTS[16], SHADOW_EXPECTED_RESULTS[16], "Q16")


def test_17_query_17(cursor, shadow_cursor):
    """
    Query 17

    Among research users with at least two reservations, list those whose latest reservation was within the last fourteen days.
    """
    sql = """
    SELECT PersonID FROM Reservation GROUP BY PersonID HAVING COUNT(*) >= 2 AND MAX(PlannedStartTime) >= CURDATE() - INTERVAL 14 DAY AND MAX(PlannedStartTime) < CURDATE()
    """
    assert_matches_expected(cursor, shadow_cursor, sql, EXPECTED_RESULTS[17], SHADOW_EXPECTED_RESULTS[17], "Q17")


def test_18_query_18(cursor, shadow_cursor):
    """
    Query 18

    For each building, rank laboratories by the number of approved reservations in the last ninety days.
    """
    sql = """
    SELECT l.Building, eu.LabID, COUNT(*), RANK() OVER (PARTITION BY l.Building ORDER BY COUNT(*) DESC) FROM Reservation r JOIN EquipmentUnit eu ON r.SerialNumber = eu.SerialNumber JOIN Laboratory l ON eu.LabID = l.LabID WHERE r.Status = 'Approved' AND r.PlannedStartTime >= CURDATE() - INTERVAL 90 DAY AND r.PlannedStartTime < CURDATE() GROUP BY l.Building, eu.LabID
    """
    assert_matches_expected(cursor, shadow_cursor, sql, EXPECTED_RESULTS[18], SHADOW_EXPECTED_RESULTS[18], "Q18")


def test_19_query_19(cursor, shadow_cursor):
    """
    Query 19

    Within each building, return the equipment categories whose prices show a spread greater than thirty percent of the minimum (excluding any unit with a non-positive cost -- see Query 20).
    """
    sql = """
    SELECT l.Building, em.Category FROM Laboratory l JOIN EquipmentUnit eu ON eu.LabID = l.LabID JOIN EquipmentModel em ON em.ModelID = eu.ModelID WHERE eu.PurchaseCost > 0 GROUP BY l.Building, em.Category HAVING MAX(eu.PurchaseCost) > 1.3 * MIN(eu.PurchaseCost)
    """
    assert_matches_expected(cursor, shadow_cursor, sql, EXPECTED_RESULTS[19], SHADOW_EXPECTED_RESULTS[19], "Q19")


def test_20_query_20(cursor, shadow_cursor):
    """
    Query 20

    Data quality check: list equipment units with missing status, invalid acquisition dates, or non positive purchase cost.
    """
    sql = """
    SELECT SerialNumber FROM EquipmentUnit WHERE CurrentStatus IS NULL OR AcquisitionDate IS NULL OR AcquisitionDate > CURDATE() OR PurchaseCost IS NULL OR PurchaseCost <= 0
    """
    assert_matches_expected(cursor, shadow_cursor, sql, EXPECTED_RESULTS[20], SHADOW_EXPECTED_RESULTS[20], "Q20")
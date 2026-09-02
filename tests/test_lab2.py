import os
import pymysql
import pytest


# CONFIG
DB_NAME = "RLMS_LAB2"


@pytest.fixture(scope="session")
def connection():
    conn = pymysql.connect(
        host="127.0.0.1",
        user="root",
        password="root",
        autocommit=True,
    )
    yield conn
    conn.close()


@pytest.fixture(scope="session", autouse=True)
def setup_database(connection):
   
    cur = connection.cursor()
    cur.execute(f"DROP DATABASE IF EXISTS {DB_NAME}")
    cur.execute(f"CREATE DATABASE {DB_NAME}")
    cur.execute(f"USE {DB_NAME}")
    cur.close()
    yield


@pytest.fixture
def cursor(connection, setup_database):
    cur = connection.cursor()
    cur.execute(f"USE {DB_NAME}")
    yield cur
    cur.close()



# ============================================================================
# INFORMATION_SCHEMA introspection 
# ============================================================================

def _table_exists(cur, table_name):
    cur.execute(
        "SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES "
        "WHERE TABLE_SCHEMA = %s AND LOWER(TABLE_NAME) = LOWER(%s)",
        (DB_NAME, table_name),
    )
    return cur.fetchone()[0] > 0


def _actual_columns(cur, table_name):
    cur.execute(
        "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS "
        "WHERE TABLE_SCHEMA = %s AND LOWER(TABLE_NAME) = LOWER(%s)",
        (DB_NAME, table_name),
    )
    return {row[0].lower() for row in cur.fetchall()}


def _actual_primary_key(cur, table_name):
    cur.execute(
        "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE "
        "WHERE TABLE_SCHEMA = %s AND LOWER(TABLE_NAME) = LOWER(%s) "
        "AND CONSTRAINT_NAME = 'PRIMARY'",
        (DB_NAME, table_name),
    )
    return {row[0].lower() for row in cur.fetchall()}


def _actual_foreign_keys(cur, table_name):
    cur.execute(
        "SELECT COLUMN_NAME, REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME "
        "FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE "
        "WHERE TABLE_SCHEMA = %s AND LOWER(TABLE_NAME) = LOWER(%s) "
        "AND REFERENCED_TABLE_NAME IS NOT NULL",
        (DB_NAME, table_name),
    )
    return {(col.lower(), ref_t.lower(), ref_c.lower()) for col, ref_t, ref_c in cur.fetchall()}


def assert_table_matches_expected(cursor, sql, table_name):
    cursor.execute(sql)

    expected = EXPECTED_SCHEMA[table_name]

    if not _table_exists(cursor, table_name):
        pytest.fail(
            f"No table named '{table_name}' was found after running your "
            f"SQL -- check your CREATE TABLE statement uses this exact "
            f"table name."
        )

    expected_columns = {c.lower() for c in expected["columns"]}
    actual_columns = _actual_columns(cursor, table_name)
    missing_columns = expected_columns - actual_columns
    extra_columns = actual_columns - expected_columns

    expected_pk = {c.lower() for c in expected["primary_key"]}
    actual_pk = _actual_primary_key(cursor, table_name)

    expected_fks = {(c.lower(), t.lower(), r.lower()) for c, t, r in expected["foreign_keys"]}
    actual_fks = _actual_foreign_keys(cursor, table_name)
    missing_fks = expected_fks - actual_fks
    extra_fks = actual_fks - expected_fks

    problems = []
    if missing_columns:
        problems.append(f"missing column(s): {sorted(missing_columns)}")
    if extra_columns:
        problems.append(f"unexpected extra column(s): {sorted(extra_columns)}")
    if actual_pk != expected_pk:
        problems.append(
            f"primary key mismatch -- expected {sorted(expected_pk)}, "
            f"got {sorted(actual_pk)}"
        )
    if missing_fks:
        readable = [f"{c} -> {t}({r})" for c, t, r in sorted(missing_fks)]
        problems.append(f"missing foreign key(s): {readable}")
    if extra_fks:
        readable = [f"{c} -> {t}({r})" for c, t, r in sorted(extra_fks)]
        problems.append(f"unexpected foreign key(s): {readable}")

    if problems:
        pytest.fail(f"Table '{table_name}': " + "; ".join(problems))


# ============================================================================
# TESTS
# ============================================================================

def test_01_create_person(cursor):
    """
    Exercise 1: Person

    Create the Person table, based on the ER model.
    """
    sql = """
    -- WRITE YOUR SQL HERE
    """
    assert_table_matches_expected(cursor, sql, "Person")


def test_02_create_serviceprovider(cursor):
    """
    Exercise 2: ServiceProvider

    Create the ServiceProvider table, based on the ER model.
    """
    sql = """
    -- WRITE YOUR SQL HERE
    """
    assert_table_matches_expected(cursor, sql, "ServiceProvider")


def test_03_create_researchproject(cursor):
    """
    Exercise 3: ResearchProject

    Create the ResearchProject table, based on the ER model.
    """
    sql = """
    -- WRITE YOUR SQL HERE
    """
    assert_table_matches_expected(cursor, sql, "ResearchProject")


def test_04_create_equipmentmodel(cursor):
    """
    Exercise 4: EquipmentModel

    Create the EquipmentModel table, based on the ER model.
    """
    sql = """
    -- WRITE YOUR SQL HERE
    """
    assert_table_matches_expected(cursor, sql, "EquipmentModel")


def test_05_create_certification(cursor):
    """
    Exercise 5: Certification

    Create the Certification table, based on the ER model.
    """
    sql = """
    -- WRITE YOUR SQL HERE
    """
    assert_table_matches_expected(cursor, sql, "Certification")


def test_06_create_consumable(cursor):
    """
    Exercise 6: Consumable

    Create the Consumable table, based on the ER model.
    """
    sql = """
    -- WRITE YOUR SQL HERE
    """
    assert_table_matches_expected(cursor, sql, "Consumable")


def test_07_create_researchuser(cursor):
    """
    Exercise 7: ResearchUser

    Create the ResearchUser table, based on the ER model.
    """
    sql = """
    -- WRITE YOUR SQL HERE
    """
    assert_table_matches_expected(cursor, sql, "ResearchUser")


def test_08_create_technicalstaff(cursor):
    """
    Exercise 8: TechnicalStaff

    Create the TechnicalStaff table, based on the ER model.
    """
    sql = """
    -- WRITE YOUR SQL HERE
    """
    assert_table_matches_expected(cursor, sql, "TechnicalStaff")


def test_09_create_laboratory(cursor):
    """
    Exercise 9: Laboratory

    Create the Laboratory table, based on the ER model.
    """
    sql = """
    -- WRITE YOUR SQL HERE
    """
    assert_table_matches_expected(cursor, sql, "Laboratory")


def test_10_create_internaltechnician(cursor):
    """
    Exercise 10: InternalTechnician

    Create the InternalTechnician table, based on the ER model.
    """
    sql = """
    -- WRITE YOUR SQL HERE
    """
    assert_table_matches_expected(cursor, sql, "InternalTechnician")


def test_11_create_externaltechnician(cursor):
    """
    Exercise 11: ExternalTechnician

    Create the ExternalTechnician table, based on the ER model.
    """
    sql = """
    -- WRITE YOUR SQL HERE
    """
    assert_table_matches_expected(cursor, sql, "ExternalTechnician")


def test_12_create_attachedto(cursor):
    """
    Exercise 12: AttachedTo

    Create the AttachedTo table, based on the ER model.
    """
    sql = """
    -- WRITE YOUR SQL HERE
    """
    assert_table_matches_expected(cursor, sql, "AttachedTo")


def test_13_create_projectparticipation(cursor):
    """
    Exercise 13: ProjectParticipation

    Create the ProjectParticipation table, based on the ER model.
    """
    sql = """
    -- WRITE YOUR SQL HERE
    """
    assert_table_matches_expected(cursor, sql, "ProjectParticipation")


def test_14_create_equipmentunit(cursor):
    """
    Exercise 14: EquipmentUnit

    Create the EquipmentUnit table, based on the ER model.
    """
    sql = """
    -- WRITE YOUR SQL HERE
    """
    assert_table_matches_expected(cursor, sql, "EquipmentUnit")


def test_15_create_holdscertification(cursor):
    """
    Exercise 15: HoldsCertification

    Create the HoldsCertification table, based on the ER model.
    """
    sql = """
    -- WRITE YOUR SQL HERE
    """
    assert_table_matches_expected(cursor, sql, "HoldsCertification")


def test_16_create_requirescertification(cursor):
    """
    Exercise 16: RequiresCertification

    Create the RequiresCertification table, based on the ER model.
    """
    sql = """
    -- WRITE YOUR SQL HERE
    """
    assert_table_matches_expected(cursor, sql, "RequiresCertification")


def test_17_create_stores(cursor):
    """
    Exercise 17: Stores

    Create the Stores table, based on the ER model.
    """
    sql = """
    -- WRITE YOUR SQL HERE
    """
    assert_table_matches_expected(cursor, sql, "Stores")


def test_18_create_reservation(cursor):
    """
    Exercise 18: Reservation

    Create the Reservation table, based on the ER model.
    """
    sql = """
    -- WRITE YOUR SQL HERE
    """
    assert_table_matches_expected(cursor, sql, "Reservation")


def test_19_create_maintenance(cursor):
    """
    Exercise 19: Maintenance

    Create the Maintenance table, based on the ER model.
    """
    sql = """
    -- WRITE YOUR SQL HERE
    """
    assert_table_matches_expected(cursor, sql, "Maintenance")


def test_20_create_calibrationrecord(cursor):
    """
    Exercise 20: CalibrationRecord

    Create the CalibrationRecord table, based on the ER model.
    """
    sql = """
    -- WRITE YOUR SQL HERE
    """
    assert_table_matches_expected(cursor, sql, "CalibrationRecord")


def test_21_create_usagesession(cursor):
    """
    Exercise 21: UsageSession

    Create the UsageSession table, based on the ER model.
    """
    sql = """
    -- WRITE YOUR SQL HERE
    """
    assert_table_matches_expected(cursor, sql, "UsageSession")


def test_22_create_consumes(cursor):
    """
    Exercise 22: Consumes

    Create the Consumes table, based on the ER model.
    """
    sql = """
    -- WRITE YOUR SQL HERE
    """
    assert_table_matches_expected(cursor, sql, "Consumes")
from django.db import migrations


def _forwards(apps, schema_editor):
    """Make `django_admin_log.user_id` unsigned bigint and add FK to users(id) only if required."""
    conn = schema_editor.connection
    table = 'django_admin_log'
    col = 'user_id'
    ref_table = 'users'
    ref_col = 'id'
    desired_name = 'django_admin_log_user_id_fk_users_id'
    with conn.cursor() as cursor:
        # Check current column type
        cursor.execute(
            "SELECT COLUMN_TYPE FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME=%s AND COLUMN_NAME=%s",
            [table, col],
        )
        row = cursor.fetchone()
        is_unsigned = False
        if row:
            coltype = row[0] or ''
            is_unsigned = 'unsigned' in coltype.lower()

        # Check whether a FK to users(id) already exists
        cursor.execute(
            "SELECT CONSTRAINT_NAME FROM information_schema.KEY_COLUMN_USAGE "
            "WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME=%s AND COLUMN_NAME=%s "
            "AND REFERENCED_TABLE_NAME=%s AND REFERENCED_COLUMN_NAME=%s",
            [table, col, ref_table, ref_col],
        )
        fk_row = cursor.fetchone()
        has_fk = bool(fk_row)

        # If column not unsigned, alter it
        if not is_unsigned:
            cursor.execute("ALTER TABLE `" + table + "` MODIFY COLUMN `" + col + "` bigint(20) unsigned NOT NULL;")

        # If FK not present, add it (use a deterministic name if not existing)
        if not has_fk:
            # ensure the chosen constraint name is not already used
            cursor.execute(
                "SELECT CONSTRAINT_NAME FROM information_schema.TABLE_CONSTRAINTS "
                "WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME=%s AND CONSTRAINT_NAME=%s",
                [table, desired_name],
            )
            if not cursor.fetchone():
                cursor.execute(
                    "ALTER TABLE `" + table + "` ADD CONSTRAINT `%s` FOREIGN KEY (`" + col + "`) REFERENCES `" + ref_table + "` (`" + ref_col + "`);" % desired_name
                )


def _backwards(apps, schema_editor):
    """Drop the FK to users(id) if present and revert column to signed bigint."""
    conn = schema_editor.connection
    table = 'django_admin_log'
    col = 'user_id'
    ref_table = 'users'
    ref_col = 'id'
    with conn.cursor() as cursor:
        # Find FK constraint referencing users(id)
        cursor.execute(
            "SELECT CONSTRAINT_NAME FROM information_schema.KEY_COLUMN_USAGE "
            "WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME=%s AND COLUMN_NAME=%s "
            "AND REFERENCED_TABLE_NAME=%s AND REFERENCED_COLUMN_NAME=%s",
            [table, col, ref_table, ref_col],
        )
        fk_row = cursor.fetchone()
        if fk_row:
            fk_name = fk_row[0]
            # Drop FK
            cursor.execute("ALTER TABLE `" + table + "` DROP FOREIGN KEY `" + fk_name + "`;")

        # Revert column to signed bigint if currently unsigned
        cursor.execute(
            "SELECT COLUMN_TYPE FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME=%s AND COLUMN_NAME=%s",
            [table, col],
        )
        row = cursor.fetchone()
        if row:
            coltype = row[0] or ''
            if 'unsigned' in coltype.lower():
                cursor.execute("ALTER TABLE `" + table + "` MODIFY COLUMN `" + col + "` bigint(20) NOT NULL;")


class Migration(migrations.Migration):

    dependencies = [
        ('admin', '0003_logentry_add_action_flag_choices'),
        ('bookings', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(_forwards, _backwards),
    ]

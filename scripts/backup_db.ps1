# scripts/backup_db.ps1
$DB_NAME   = "fastfood24_db"
$DB_USER   = "postgres"
$DB_HOST   = "localhost"
$DB_PORT   = "5432"
$DB_PASS   = "postgres"  # ⚠️ Для продакшена лучше использовать .pgpass

$BACKUP_DIR = "E:\fastfood24\backups"
$DATE       = Get-Date -Format "yyyyMMdd_HHmm"
$BACKUP_FILE = "$BACKUP_DIR\backup_$DATE.sql"
$LOG_FILE   = "$BACKUP_DIR\backup_log.txt"

# Создаём папку бэкапов, если её нет
if (!(Test-Path $BACKUP_DIR)) { New-Item -ItemType Directory -Path $BACKUP_DIR | Out-Null }

# Передаём пароль в сессию (без этого pg_dump запросит ввод вручную)
$env:PGPASSWORD = $DB_PASS

try {
    $PG_DUMP = "pg_dump"

    Write-Output "[$(Get-Date)] Start of backup..." | Out-File $LOG_FILE -Append

    & $PG_DUMP -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -F p -f $BACKUP_FILE

    if ($LASTEXITCODE -eq 0) {
        $Size = (Get-Item $BACKUP_FILE).Length / 1MB
        Write-Output "[$(Get-Date)] Success: $BACKUP_FILE (${Size:N2} МБ)" | Out-File $LOG_FILE -Append
    } else {
        Write-Output "[$(Get-Date)] Error while creating a dump! Code: $LASTEXITCODE" | Out-File $LOG_FILE -Append
        exit 1
    }
} finally {
    $env:PGPASSWORD = $null # Очищаем пароль из памяти
}

# Очистка бэкапов старше 30 дней
$CutoffDate = (Get-Date).AddDays(-30)

# Сначала находим старые файлы, а потом удаляем
$OldBackups = Get-ChildItem -Path $BACKUP_DIR -Filter "backup_*.sql" | Where-Object { $_.CreationTime -lt $CutoffDate }

if ($OldBackups) {
    $OldBackups | Remove-Item -Force
    Write-Output "[$(Get-Date)] CLEANED: Older backups deleted: $($OldBackups.Count)" | Out-File $LOG_FILE -Append
} else {
    Write-Output "[$(Get-Date)] OK: No old backups for delete found." | Out-File $LOG_FILE -Append
}
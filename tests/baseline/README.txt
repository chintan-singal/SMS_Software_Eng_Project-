SMS testing evidence | 20 November 2026, India local time

Start with verification/results.json. It records the environment, per-case expectations and observations, and final MySQL reads. verification/server.log captures the HTTP requests and the missing-template traceback. The two PNGs show Edge rendering the real student portal. verification/console.txt is the verification run's console output. B01 was blocked before execution and appears in the JSON, not the HTTP log.

run_qa.py is the executable suite, fixture.sql supplies the schema extensions and synthetic rows, and requirements.txt pins the installed Python packages. The Python and HTML under test come from the original SMS-DBS-master.zip, supplied separately. The runner creates a new schema and an output directory per run. It checks the connected server's actual data directory before creating the schema.

Reproduce on Windows with Python 3.11, MySQL Community Server 8.0 and Microsoft Edge installed. Use two PowerShell windows in this extracted evidence folder. Select a free loopback port and a new, empty data directory; the examples use port 38462. Only the disposable local instance below uses a blank root password.

1. Prepare dependencies in the first window.
   python -m venv .qa-venv
   & ./.qa-venv/Scripts/python.exe -m pip install -r requirements.txt

2. Initialize and start the disposable database in that same window.
   $qaData = Join-Path $env:TEMP ('sms-qa-' + [Guid]::NewGuid().ToString('N'))
   New-Item -ItemType Directory -Path $qaData
   $qaData | Set-Content .qa-datadir.txt
   $serverExe = 'C:/Program Files/MySQL/MySQL Server 8.0/bin/mysqld.exe'
   & $serverExe --no-defaults --initialize-insecure "--datadir=$qaData" --console
   & $serverExe --no-defaults "--datadir=$qaData" --port=38462 --bind-address=127.0.0.1 --mysqlx=0 --skip-log-bin --default-time-zone=+00:00 --console

3. In the second window, use the original project archive and a fresh output path.
   $qaData = Get-Content .qa-datadir.txt
   $archive = Join-Path $env:USERPROFILE 'Downloads/SMS-DBS-master.zip'
   $qaOut = 'run-' + [Guid]::NewGuid().ToString('N')
   & ./.qa-venv/Scripts/python.exe run_qa.py --zip $archive --datadir $qaData --port 38462 --out $qaOut
   Get-Content (Join-Path $qaOut 'results.json')

4. End this disposable server using its dedicated port.
   & 'C:/Program Files/MySQL/MySQL Server 8.0/bin/mysqladmin.exe' --no-defaults --protocol=tcp --host=127.0.0.1 --port=38462 --user=root shutdown

The verified baseline produced 23 PASS, 3 FAIL and 1 BLOCKED. Inspect the individual statuses in results.json; the runner records assertion failures and continues to later cases. The sample assignment and certificate workflows depend on initially empty workflow tables. The program reads IDs from the normal forms for the cross-portal journeys. Case I13 runs after S04 and examines the first task in its fresh fixture.

The archive lacked a gateway and database export. The runner uses genuine Flask handlers, Jinja templates, MySQL connectors and SQL, with driver connection settings redirected during import and separate role sessions. Unit checks use isolated request contexts and selected test doubles. Driver overrides, SQL fixtures and browser navigation are visible in run_qa.py. Re-run the release package against its canonical schema when supplied.

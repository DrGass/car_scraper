USE mgr_aplikacja
GO

BULK INSERT dbo.dane
FROM '' --Prosz� wstawi� �ci�k� do pliku dane_all.csv
WITH(
	CODEPAGE = 'ACP',
	FIRSTROW = 2,
	FIELDTERMINATOR = ';',
	ROWTERMINATOR = '\n'
)
GO

CREATE DATABASE mgr_aplikacja
GO

USE mgr_aplikacja
GO

SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [dbo].[dane](
	[marka] [varchar](50) NULL,
	[model] [varchar](50) NULL,
	[rok_prod] [smallint] NULL,
	[paliwo] [varchar](50) NULL,
	[przebieg] [varchar](50) NULL,
	[pojemnosc] [varchar](50) NULL,
	[skr_bie] [varchar](50) NULL,
	[kolor] [varchar](50) NULL,
	[stan] [varchar](50) NULL,
	[cena] [int] NULL,
	[kraj] [varchar](50) NULL,
	[link] [varchar](5000) NULL
) ON [PRIMARY]
GO
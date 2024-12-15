DROP TABLE IF EXISTS DailyInventoryLevels;
CREATE TABLE DailyInventoryLevels AS
WITH MostRecentInventory AS (
  SELECT 
    ProductID,
    MAX(DATE(ModifiedDate)) AS MostRecentDate,
    Quantity AS MostRecentQuantity
  FROM ProductInventory
  GROUP BY ProductID
),

RelevantTransactions AS (
  SELECT 
    th.ProductID,
    DATE(th.TransactionDate) AS TransactionDate,
    CASE 
      WHEN th.TransactionType = 'P' THEN th.Quantity   -- Positive for purchases
      ELSE -th.Quantity                                -- Negative for other transactions (e.g., sales)
    END AS Adjustment
  FROM TransactionHistory th
  WHERE th.TransactionDate <= (
    SELECT MAX(DATE(ModifiedDate)) 
    FROM ProductInventory
    WHERE ProductID = th.ProductID
  )
),

ReverseInventory AS (
  SELECT 
    t.ProductID,
    t.TransactionDate,
    SUM(t.Adjustment) 
      OVER (PARTITION BY t.ProductID ORDER BY t.TransactionDate DESC) AS CumulativeAdjustment
  FROM RelevantTransactions t
  JOIN MostRecentInventory mr
    ON t.ProductID = mr.ProductID
),

FinalInventory AS (
  SELECT 
    mr.ProductID,
    rt.TransactionDate,
    mr.MostRecentQuantity + rt.CumulativeAdjustment AS CalculatedInventory
  FROM MostRecentInventory mr
  JOIN ReverseInventory rt
    ON mr.ProductID = rt.ProductID
)

SELECT 
  ProductID,
  TransactionDate,
  CalculatedInventory
FROM FinalInventory
ORDER BY ProductID, TransactionDate DESC;


CREATE TABLE ProductFillRate AS
WITH DailyDemand AS (
  SELECT 
    DATE(tb1.OrderDate) AS OrderDate,
    tb2.ProductID,
    SUM(tb2.OrderQty) AS Demand
  FROM "SalesOrderHeader" tb1
  LEFT JOIN "SalesOrderDetail" tb2
    ON tb1.SalesOrderId = tb2.SalesOrderId
  GROUP BY tb1.OrderDate, tb2.ProductID
)

SELECT 
  tb1.OrderDate,
  tb1.ProductID,
  tb1.Demand,
  COALESCE(tb2.CumulativeInventory, 0) AS CumulativeInventory,
  CASE 
    WHEN tb2.CumulativeInventory IS NULL OR tb2.CumulativeInventory = 0 THEN 0.00
    ELSE CAST(tb1.Demand AS REAL) / tb2.CumulativeInventory
  END AS FillRate
FROM DailyDemand tb1
LEFT JOIN DailyInventoryLevels tb2
  ON tb1.OrderDate = tb2.InventoryDate
ORDER BY tb1.OrderDate, tb1.ProductID



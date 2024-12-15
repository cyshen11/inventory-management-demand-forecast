DROP TABLE IF EXISTS ProductFillRate;
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
  COALESCE(SUM(tb2.Quantity), 0) AS CumulativeInventory,
  CASE 
    WHEN COALESCE(SUM(tb2.Quantity), 0) = 0 THEN 0.00
    ELSE CAST(tb1.Demand AS REAL) / SUM(tb2.Quantity)
  END AS FillRate
FROM DailyDemand tb1
LEFT JOIN ProductInventory tb2
  ON tb1.ProductID = tb2.ProductID
GROUP BY 
  tb1.OrderDate,
  tb1.ProductID,
  tb1.Demand
ORDER BY tb1.OrderDate, tb1.ProductID



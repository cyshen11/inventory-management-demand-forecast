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
),

DemandAndInventory AS (
  SELECT 
    dd.OrderDate,
    dd.ProductID,
    dd.Demand,
    COALESCE(di.CalculatedInventory, 0) AS CalculatedInventory
  FROM DailyDemand dd
  LEFT JOIN DailyInventoryLevels di
  ON
    dd.ProductID = di.ProductID
    AND dd.OrderDate = di.TransactionDate
)

SELECT
  OrderDate,
  ProductID,
  Demand,
  CalculatedInventory,
  CASE 
    WHEN COALESCE(CalculatedInventory , 0) = 0 THEN 0.00
    ELSE CAST(Demand AS REAL) / CalculatedInventory
  END AS FillRate
FROM DemandAndInventory
ORDER BY OrderDate, ProductID



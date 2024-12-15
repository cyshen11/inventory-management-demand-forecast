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

LatestInventory AS (
  SELECT 
    di.ProductID,
    di.TransactionDate,
    di.CalculatedInventory,
    ROW_NUMBER() OVER (
      PARTITION BY di.ProductID
      ORDER BY di.TransactionDate DESC
    ) AS Rank
  FROM DailyInventoryLevels di
  WHERE di.TransactionDate <= (
    SELECT OrderDate FROM DailyDemand dd WHERE di.ProductID = dd.ProductID
  )
),

DemandAndInventory AS (
  SELECT 
    dd.OrderDate,
    dd.ProductID,
    dd.Demand,
    COALESCE(
        (SELECT CalculatedInventory 
        FROM LatestInventory li 
        WHERE dd.ProductID = li.ProductID 
          AND li.TransactionDate <= dd.OrderDate
        ORDER BY li.TransactionDate DESC
        LIMIT 1),
        0
    ) AS CalculatedInventory
  FROM DailyDemand dd
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



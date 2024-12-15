DROP TABLE IF EXISTS OrderFillRate;

CREATE TABLE OrderFillRate AS
WITH DailyDemand AS (
  SELECT 
    tb1.SalesOrderID,
    DATE(tb1.OrderDate) AS OrderDate,
    tb2.ProductID,
    tb2.OrderQty AS Demand
  FROM "SalesOrderHeader" tb1
  LEFT JOIN "SalesOrderDetail" tb2
    ON tb1.SalesOrderID = tb2.SalesOrderID
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
    dd.SalesOrderID,
    dd.OrderDate,
    dd.ProductID,
    dd.Demand,
    COALESCE(
      (SELECT li.CalculatedInventory 
       FROM LatestInventory li 
       WHERE dd.ProductID = li.ProductID 
         AND li.TransactionDate <= dd.OrderDate
       ORDER BY li.TransactionDate DESC
       LIMIT 1),
      0
    ) AS CalculatedInventory,
    CASE
      WHEN dd.Demand > COALESCE(
        (SELECT li.CalculatedInventory 
         FROM LatestInventory li 
         WHERE dd.ProductID = li.ProductID 
           AND li.TransactionDate <= dd.OrderDate
         ORDER BY li.TransactionDate DESC
         LIMIT 1),
        0
      ) THEN 1
      ELSE 0
    END AS DemandGtInv
  FROM DailyDemand dd
)

SELECT 
  SalesOrderID,
  OrderDate,
  CASE WHEN
    MAX(DemandGtInv) = 1 THEN 0 -- Order not filled
    ELSE 1 -- Order filled
  END IsOrderFilled
FROM DemandAndInventory
GROUP BY SalesOrderID, OrderDate
ORDER BY SalesOrderID;

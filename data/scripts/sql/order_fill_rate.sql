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

DemandAndInventory AS (
  SELECT 
    dd.SalesOrderID,
    dd.OrderDate,
    dd.ProductID,
    dd.Demand,
    COALESCE(di.CalculatedInventory, 0) AS CalculatedInventory,
    CASE
      WHEN dd.Demand > COALESCE(di.CalculatedInventory, 0) THEN 1
      ELSE 0
    END AS DemandGtInv
  FROM DailyDemand dd
  LEFT JOIN DailyInventoryLevels di
    ON dd.ProductID = di.ProductID
    AND dd.OrderDate = di.TransactionDate
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

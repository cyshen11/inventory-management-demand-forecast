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
    ON tb1.SalesOrderId = tb2.SalesOrderId
),

DemandAndInventory AS (
  SELECT 
    tb1.SalesOrderID,
    tb1.OrderDate,
    tb1.ProductID,
    tb1.Demand,
    COALESCE(SUM(tb2.Quantity), 0) AS CumulativeInventory,
    CASE
      WHEN tb1.Demand > COALESCE(SUM(tb2.Quantity), 0) THEN 1
      ELSE 0
    END AS DemandGtInv
  FROM DailyDemand tb1
  LEFT JOIN ProductInventory tb2
    ON tb1.ProductID = tb2.ProductID
  GROUP BY 
    tb1.SalesOrderID,
    tb1.OrderDate,
    tb1.ProductID,
    tb1.Demand
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
ORDER BY SalesOrderID



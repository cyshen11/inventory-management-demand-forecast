-- Step 1: Create a CTE for the initial inventory levels
CREATE TABLE DailyInventoryLevels AS
WITH InitialInventory AS (
  SELECT 
    ProductID,
    DATE(ModifiedDate) AS InventoryDate,
    SUM(Quantity) AS InitialQuantity
  FROM ProductInventory
  GROUP BY ProductID, DATE(ModifiedDate)
),

-- Step 2: Create a CTE for daily transaction adjustments
DailyTransactions AS (
  SELECT 
    ProductID,
    DATE(TransactionDate) AS TransactionDate,
    SUM(CASE 
          WHEN TransactionType = 'P' THEN Quantity   -- Positive for purchases (P)
          ELSE -Quantity                               -- Negative for other transaction types (e.g., sales)
        END) AS TransactionAdjustment
  FROM TransactionHistory
  GROUP BY ProductID, DATE(TransactionDate)
),

-- Step 3: Generate all possible dates by unioning inventory and transaction dates
AllDates AS (
  SELECT DISTINCT DATE(ModifiedDate) AS Date
  FROM ProductInventory
  UNION
  SELECT DISTINCT DATE(TransactionDate) AS Date
  FROM TransactionHistory
),

-- Step 4: Calculate daily inventory levels
DailyInventory AS (
  SELECT 
    ad.Date AS InventoryDate,
    pi.ProductID,
    COALESCE(SUM(ii.InitialQuantity), 0) AS InitialQuantity,
    COALESCE(SUM(dt.TransactionAdjustment), 0) AS DailyTransaction
  FROM AllDates ad
  CROSS JOIN (SELECT DISTINCT ProductID FROM ProductInventory) pi
  LEFT JOIN InitialInventory ii
    ON pi.ProductID = ii.ProductID AND ad.Date = ii.InventoryDate
  LEFT JOIN DailyTransactions dt
    ON pi.ProductID = dt.ProductID AND ad.Date = dt.TransactionDate
  GROUP BY ad.Date, pi.ProductID
),

-- Step 5: Calculate cumulative inventory levels
DailyCumulativeInventory AS (
  SELECT 
    di.InventoryDate,
    di.ProductID,
    SUM(di.InitialQuantity + di.DailyTransaction) 
      OVER (PARTITION BY di.ProductID ORDER BY di.InventoryDate) AS CumulativeInventory
  FROM DailyInventory di
  ORDER BY di.ProductID, di.InventoryDate
)

SELECT * FROM DailyCumulativeInventory
WHERE CumulativeInventory > 0

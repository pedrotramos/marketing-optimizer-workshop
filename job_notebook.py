# Databricks notebook source
dbutils.widgets.text("baseline_profit", "0.0", "Baseline Profit")
dbutils.widgets.text("total_budget", "0.0", "Total Budget")
dbutils.widgets.text("constraints", "{}", "Constraints")
dbutils.widgets.text("baseline_spend", "{}", "Baseline Spend")
dbutils.widgets.text("run_id", "", "Run ID")
dbutils.widgets.text("catalog", "", "Catalog")
dbutils.widgets.text("schema", "", "Schema")

baseline_profit = float(dbutils.widgets.get("baseline_profit"))
total_budget = float(dbutils.widgets.get("total_budget"))
constraints = eval(dbutils.widgets.get("constraints"))
baseline_spend = eval(dbutils.widgets.get("baseline_spend"))
run_id = dbutils.widgets.get("run_id")
catalog = dbutils.widgets.get("catalog")
schema = dbutils.widgets.get("schema")

# COMMAND ----------

import random

# Generate random spend for each channel within constraints, not exceeding total_budget
random_spend = {}
remaining_budget = total_budget
channels = list(baseline_spend.keys())

for i, channel in enumerate(channels):
    c = constraints.get(channel, (1.0, 1.0))
    if i == len(channels) - 1:
      # Assign remaining budget to last channel, but not less than min or more than max
      spend = min(max(baseline_spend[channel] * ((100 + c["min"]) / 100), remaining_budget), baseline_spend[channel] * ((100 + c["max"]) / 100))
    else:
      factor = random.uniform(100 + c["min"], 100 + c["max"])
      spend = min(baseline_spend[channel] * (factor / 100), remaining_budget)
    random_spend[channel] = spend
    remaining_budget -= spend
    if remaining_budget <= 0:
      break

# COMMAND ----------

ret = random.uniform(0.01, 0.08)
new_profit = baseline_profit * (1 + ret)
new_investment = sum(random_spend.values())
print(f"New investment: {new_investment}")
print(f"New profit: {new_profit}")
print(f"Random spend: {random_spend}")
print(f"Return: {ret}")

# COMMAND ----------

df = spark.createDataFrame([(run_id, new_investment, new_profit, random_spend)], ["id", "investimento_total", "lucro_bruto", "investimento_por_canal"])
df.display()
df.write.mode("append").saveAsTable(f"{catalog}.{schema}.resultados_simulacao")

# COMMAND ----------

spark.sql(f"ALTER TABLE {catalog}.{schema}.`resultados_simulacao` SET TBLPROPERTIES (delta.enableChangeDataFeed = true)")

# COMMAND ----------


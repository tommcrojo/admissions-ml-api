# Databricks Notebook - Python

# Command 1
df = (spark.read
      .option("header", "true")
      .option("inferSchema", "true")
      .option("delimiter", ",")  
      .csv("/Volumes/workspace/bronze/synthetic_data/admissions_synthetic_ucam2.csv"))

# Command 2
spark.sql("CREATE DATABASE IF NOT EXISTS bronze")
df.write.mode("overwrite").saveAsTable("bronze.admissions_raw")


# Command 3
display(spark.table("bronze.admissions_raw"))


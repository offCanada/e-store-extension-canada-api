import duckdb
import os

# create a connection
con = duckdb.connect('./database/nutrilens.duckdb')

# connection check
if not con:
    raise RuntimeError("Couldn't connect to Database")

# remove all existing tables to avoid conflicts
tables = con.sql("SHOW TABLES").fetchall()
for (table,) in tables:
    con.execute(f'DROP TABLE IF EXISTS "{table}"')

# gather all parquet files and create their table with filename
folder = './database/dataset/'
for file in os.listdir(folder):
    if file.endswith('.parquet'):
        table_name = os.path.splitext(file)[0]
        con.sql(f"""
            CREATE TABLE {table_name} AS
            SELECT * FROM read_parquet('{folder}{file}')
        """)

# extracting and merging required fields into one table
con.execute("""
    CREATE TABLE product_merged AS
    SELECT
      pm.external_id, pm.upc, pm.variant_id,
      pm.reference_db_taxonomy, pm.title, pm.brand, pm.core_title, pm.image_url,
      pv.size, pn.serving_size,
      pn.normalization_method,
      CASE WHEN isnan(pn.sugars_g_per_100g) THEN NULL ELSE pn.sugars_g_per_100g END AS sugars_per_100g,
      CASE WHEN isnan(pn.sodium_mg_per_100g) THEN NULL ELSE pn.sodium_mg_per_100g END AS sodium_per_100g,
      CASE WHEN isnan(pn.fat_g_per_100g) THEN NULL ELSE pn.fat_g_per_100g END AS fat_per_100g,
      CASE WHEN isnan(pn.saturated_fat_g_per_100g) THEN NULL ELSE pn.saturated_fat_g_per_100g END AS saturated_fat_per_100g,
      ps.nutri_score_points
    FROM product_metadata pm
    LEFT JOIN product_nutrition pn ON pm.upc = pn.upc
    LEFT JOIN product_scores ps ON pm.upc = ps.upc and pm.variant_id = ps.variant_id
    LEFT JOIN product_variants pv ON pm.variant_id = pv.variant_id
    WHERE pm.product_domain = 'food'
    GROUP BY 
        pm.external_id, pm.upc, pm.variant_id, 
        pm.title, pm.core_title, pm.brand, pm.image_url, 
        pm.reference_db_taxonomy, pn.serving_size, 
        pn.sugars_g_per_100g, pn.sodium_mg_per_100g, pn.fat_g_per_100g, pn.saturated_fat_g_per_100g, pn.normalization_method, 
        ps.nutri_score_points, pv.size
    ORDER BY pm.upc
""")

# show products count
print(con.execute("SELECT COUNT(*) FROM product_merged").fetchone())

# save and close connection
con.commit()
con.close()
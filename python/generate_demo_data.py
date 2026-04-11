import json
import random
import csv
import os

def generate_products(n=1000):
    products = []
    categories = ['Electronics', 'Computing', 'Mobile', 'Gaming', 'Accessories']
    for i in range(1, n + 1):
        price = round(random.uniform(50, 2000), 2)
        old_price = round(price * random.uniform(1.05, 1.3), 2)
        products.append({
            'product_id': i,
            'name': f'Premium Product {i}',
            'category': random.choice(categories),
            'price': price,
            'old_price': old_price,
            'stock_quantity': random.randint(10, 500)
        })
    return products

def generate_specs(products):
    specs = []
    for p in products:
        spec_data = {
            "weight": f"{random.uniform(0.5, 5):.1f}kg",
            "warranty": f"{random.randint(1, 3)} years",
            "dimensions": f"{random.randint(10, 50)}x{random.randint(10, 50)}x{random.randint(5, 20)} cm"
        }
        if p['category'] == 'Computing':
            spec_data['ram'] = random.choice(['16GB', '32GB', 'Higher'])
            spec_data['cpu'] = 'High-Performance CPU'
        specs.append({'product_id': p['product_id'], 'specs': json.dumps(spec_data)})
    return specs

def generate_reviews(products, m=5):
    reviews = []
    templates = [
        "Incredibly durable product. I've used it for months and it still looks new.",
        "Good value for money, but the shipping took a bit long.",
        "Performance is top-notch. Highly recommend for enterprise use.",
        "Average build quality, but the features make up for it.",
        "The battery life is amazing. Great for on-the-go work."
    ]
    for p in products:
        for _ in range(random.randint(1, m)):
            reviews.append({
                'product_id': p['product_id'],
                'customer_name': f'Customer {random.randint(1, 10000)}',
                'review_text': random.choice(templates),
                'rating': random.randint(3, 5)
            })
    return reviews

def save_to_csv(data, filename):
    if not data: return
    keys = data[0].keys()
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        dict_writer = csv.DictWriter(f, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(data)

if __name__ == "__main__":
    print("🚀 Generating Demo Data...")
    os.makedirs('data', exist_ok=True)
    
    prods = generate_products(2000)
    specs = generate_specs(prods)
    revs = generate_reviews(prods)
    
    save_to_csv(prods, 'data/products.csv')
    save_to_csv(specs, 'data/specs.csv')
    save_to_csv(revs, 'data/reviews.csv')
    
    print(f"✅ Generated {len(prods)} products, {len(specs)} specs, and {len(revs)} reviews.")
    print("📍 Files saved in 'data/' folder.")

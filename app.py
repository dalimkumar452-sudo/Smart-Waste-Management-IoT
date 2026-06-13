from flask import Flask, render_template, jsonify, request
import random
import time

app = Flask(__name__)

# বিনগুলোর জন্য কিছু সাধারণ নাম (যেহেতু যেকোনো শহরের জন্য তৈরি হবে)
BIN_NAMES = [
    ("Main Market", "Central Zone"),
    ("Bus Terminus", "Transit Area"),
    ("Public Park", "Recreation Zone"),
    ("Hospital Road", "Medical District"),
    ("Shopping Mall", "Commercial Area"),
    ("Residential Gate", "Housing Society")
]

# ডাইনামিক ডেটা জেনারেশন ফাংশন (যে শহরে সার্চ হবে, সেখানে বিন তৈরি করবে)
def generate_live_data(center_lat, center_lng):
    live_data = []
    total_fill = 0
    full_count, warning_count, ok_count = 0, 0, 0

    for i in range(6):
        # সার্চ করা জায়গার ঠিক আশেপাশেই (±0.02 ডিগ্রি) বিনগুলো বসাবে
        b_lat = center_lat + random.uniform(-0.02, 0.02)
        b_lng = center_lng + random.uniform(-0.02, 0.02)
        name, loc = BIN_NAMES[i]
        depth = random.choice([60, 70, 80, 100])

        fill_pct = round(random.uniform(20.0, 98.0), 1)
        distance = round(depth - (depth * (fill_pct / 100)), 1)
        
        status = "OK"
        if fill_pct >= 85:
            status = "FULL"
            full_count += 1
        elif fill_pct >= 50:
            status = "MODERATE"
            warning_count += 1
        else:
            ok_count += 1

        live_data.append({
            "id": f"bin{i+1}",
            "name": name,
            "location": loc,
            "lat": round(b_lat, 5),
            "lng": round(b_lng, 5),
            "depth": depth,
            "fill_pct": fill_pct,
            "distance": distance,
            "status": status
        })
        total_fill += fill_pct

    avg_fill = round(total_fill / 6, 1) if live_data else 0
    
    return {
        "bins": live_data,
        "kpi": {
            "total": 6,
            "full": full_count,
            "warning": warning_count,
            "ok": ok_count,
            "avg_fill": avg_fill
        },
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/latest')
def get_latest_data():
    # ফ্রন্টএন্ড থেকে সার্চ করা লোকেশন নেবে, না পেলে ডিফল্ট হিসেবে 'New Delhi' দেখাবে
    lat = request.args.get('lat', default=28.6139, type=float)
    lng = request.args.get('lng', default=77.2090, type=float)
    return jsonify(generate_live_data(lat, lng))

if __name__ == '__main__':
    app.run(debug=True, port=5000)
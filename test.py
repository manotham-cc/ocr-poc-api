import requests
import concurrent.futures
import time

# 🛠️ แก้ URL ตรงนี้
URL = "https://ocr-service-api-v1-dggwhcahfca2gdc5.southeastasia-01.azurewebsites.net/extract/preview"
# 📂 เตรียมไฟล์ PDF ทดสอบสัก 1 ไฟล์ (วางไว้ที่เดียวกับ script)
TEST_FILE = "รายละเอียดพิกัดศุลกากร.pdf" 

def send_request(request_id):
    print(f"🚀 Request {request_id}: กำลังส่ง...")
    start_time = time.time()
    
    try:
        with open(TEST_FILE, 'rb') as f:
            files = {'file': (TEST_FILE, f, 'application/pdf')}
            response = requests.post(URL, files=files, timeout=600)
            
        elapsed = time.time() - start_time
        status = response.status_code
        print(f"✅ Request {request_id}: เสร็จสิ้น! (ใช้เวลา {elapsed:.2f} วินาที) [Status: {status}]")
        return elapsed
    except Exception as e:
        print(f"❌ Request {request_id}: Error - {e}")
        return 0

# เราจะยิง 4 Requests พร้อมกัน (เพื่อให้ Worker 4 ตัวทำงานพร้อมกัน)
if __name__ == "__main__":
    print(f"--- เริ่มทดสอบยิง 3 Requests พร้อมกัน (Test 3 Workers) ---")
    start_all = time.time()
    
    # max_workers=3 ฝั่ง Client ก็พอครับ ยิงไป 3 ตัวพร้อมกัน
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        # range(1, 4) จะรัน i = 1, 2, 3
        futures = [executor.submit(send_request, i) for i in range(1, 3)]
        concurrent.futures.wait(futures)

    total_time = time.time() - start_all
    print(f"\n--- สรุปผล ---")
    print(f"เวลารวมทั้งหมด: {total_time:.2f} วินาที")
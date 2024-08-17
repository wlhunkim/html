from flask import Flask, request, render_template, redirect, url_for, send_file, jsonify
import pyrebase
import json
from openpyxl import Workbook
import os

app = Flask(__name__, template_folder="public/templates")

# Firebase 설정 로드
with open('auth.json') as f:
    config = json.load(f)

# Firebase 초기화
firebase = pyrebase.initialize_app(config)
db = firebase.database()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    try:
        # 폼 데이터 가져오기
        book_name = request.form['book-name']
        author_name = request.form['author-name']
        publish_date = request.form['publish-date']

        # Realtime Database에 데이터 저장
        data = {
            "book_name": book_name,
            "author_name": author_name,
            "publish_date": publish_date
        }
        db.child("books").push(data)
        
        # 성공 메시지 반환
        return jsonify({"status": "success", "message": "도서 등록이 성공적으로 완료되었습니다."})
    except Exception as e:
        # 오류 메시지 반환
        return jsonify({"status": "error", "message": f"도서 등록에 실패했습니다: {str(e)}"})

@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/download-books')
def download_books():
    try:
        # Firebase에서 도서 목록 가져오기
        books = db.child("books").get().val()

        # 데이터가 제대로 가져와졌는지 확인하기 위해 출력
        print("Fetched data from Firebase:", books)

        if not books:
            return "도서 목록이 비어 있습니다."

        # Excel 파일 생성
        wb = Workbook()
        ws = wb.active
        ws.title = "Books"

        # 헤더 작성
        ws.append(["책 이름", "작가명", "출판 날짜"])

        # 데이터 작성
        for key, book in books.items():
            # 각 책의 데이터가 예상된 형식인지 확인
            book_name = book.get('book_name')
            author_name = book.get('author_name')
            publish_date = book.get('publish_date')
            ws.append([book_name, author_name, publish_date])

        # 파일 저장
        excel_file = "books.xlsx"
        wb.save(excel_file)

        # Excel 파일을 다운로드로 제공
        return send_file(excel_file, as_attachment=True, download_name=excel_file, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    
    except Exception as e:
        print("Error occurred:", str(e))
        return f"오류 발생: {str(e)}"


if __name__ == '__main__':
    app.run(debug=True)

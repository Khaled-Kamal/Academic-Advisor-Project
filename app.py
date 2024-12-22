from flask import Flask, render_template, request, redirect, url_for, session
import google.generativeai as genai

# إعداد مفتاح API الخاص بـ Google Generative AI
genai.configure(api_key="AIzaSyBbVz60V0nD0UqVYv_5AKYpi23IzNlw2Wg")  # ضع مفتاح API الخاص بك هنا

app = Flask(__name__)
app.secret_key = "your_secret_key"  # استخدم مفتاح سري لتأمين الجلسات

# قائمة مواد قسم IT - الفرقة الرابعة
it_courses = [
    {"id": 1, "name": "Capstone Project I", "prerequisites": ["Project Management"], "min_gpa": 2.5},
    {"id": 2, "name": "Network Analysis and Design", "prerequisites": ["Computer Networks"], "min_gpa": 2.5},
    {"id": 3, "name": "Enterprise Architecture", "prerequisites": ["Systems Analysis and Design"], "min_gpa": 2.5},
    {"id": 4, "name": "E-commerce", "prerequisites": ["Web Programming"], "min_gpa": 2.3},
    {"id": 5, "name": "Network Forensics", "prerequisites": ["Network Security"], "min_gpa": 3.0},
    {"id": 6, "name": "Parallel Computation", "prerequisites": ["Operating Systems"], "min_gpa": 3.0},
]

# صفحة تسجيل الدخول
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # تحقق بسيط من بيانات الدخول
        if username == "student" and password == "password":
            session["user"] = username  # إنشاء جلسة
            return redirect(url_for("index"))
        else:
            return render_template("login.html", error="Invalid credentials. Please try again.")

    return render_template("login.html")

# الصفحة الرئيسية
@app.route("/")
def index():
    if "user" not in session:
        return redirect(url_for("login"))  # إعادة توجيه المستخدم إلى تسجيل الدخول إذا لم يتم تسجيله
    return render_template("index.html")

@app.route("/results", methods=["POST"])
def results():
    if "user" not in session:
        return redirect(url_for("login"))  # حماية المسار
    try:
        # قراءة المدخلات من المستخدم
        gpa = float(request.form["gpa"])
        completed_courses = request.form.getlist("completed_courses")

        # تصفية المواد المتاحة بناءً على GPA والمتطلبات
        available_courses = []
        for course in it_courses:
            if all(req in completed_courses for req in course["prerequisites"]) and gpa >= course["min_gpa"]:
                available_courses.append(course["name"])

        # إعداد prompt لـ Google Generative AI
        if available_courses:
            prompt = (
                f"Based on a GPA of {gpa} and the completed courses {', '.join(completed_courses)}, "
                f"the available courses are: {', '.join(available_courses)}. Provide academic advice for the student."
            )
        else:
            prompt = (
                f"The student has a GPA of {gpa} and has completed {', '.join(completed_courses)}, "
                "but no courses are currently available. Suggest ways to improve their academic standing."
            )

        # استدعاء Google Generative AI
        response = genai.generate_content(prompt, max_output_tokens=200, temperature=0.7)

        # استخراج نص الاستجابة
        advice = response.text if response and hasattr(response, 'text') else "No advice available at this time."

        return render_template("results.html", available_courses=available_courses, advice=advice, gpa=gpa)

    except Exception as e:
        return f"حدث خطأ: {str(e)}"

@app.route("/logout")
def logout():
    session.pop("user", None)  # إنهاء الجلسة
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)

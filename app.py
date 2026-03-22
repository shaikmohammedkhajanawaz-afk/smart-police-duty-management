from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
import random

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///police_roster.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # admin or officer
    officer_id = db.Column(db.Integer, db.ForeignKey('officer.id'), nullable=True)

class Officer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    rank = db.Column(db.String(50))
    availability = db.Column(db.String(200))  # JSON or text

class Duty(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    officer_id = db.Column(db.Integer, db.ForeignKey('officer.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    shift_type = db.Column(db.String(20), nullable=False)  # day, night, emergency
    status = db.Column(db.String(20), default='assigned')  # assigned, completed

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    officer_id = db.Column(db.Integer, db.ForeignKey('officer.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), nullable=False)  # present, absent

# Create tables
with app.app_context():
    db.create_all()
    # Seed data
    if not User.query.first():
        db.session.add(User(username='admin', password='admin123', role='admin'))
        db.session.add(User(username='officer', password='officer123', role='officer', officer_id=1))
    if not Officer.query.first():
        db.session.add(Officer(name='Officer A', rank='Sergeant'))
        db.session.add(Officer(name='Officer B', rank='Constable'))
        db.session.add(Officer(name='Officer C', rank='Inspector'))
    db.session.commit()

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(username=data['username'], password=data['password'], role=data['role']).first()
    if user:
        return jsonify({'success': True, 'role': user.role, 'officer_id': user.officer_id})
    return jsonify({'success': False}), 401

@app.route('/officers', methods=['GET'])
def get_officers():
    officers = Officer.query.all()
    return jsonify([{'id': o.id, 'name': o.name, 'rank': o.rank} for o in officers])

@app.route('/duties/<int:officer_id>', methods=['GET'])
def get_duties(officer_id):
    duties = Duty.query.filter_by(officer_id=officer_id).all()
    return jsonify([{'date': str(d.date), 'shift_type': d.shift_type, 'status': d.status} for d in duties])

@app.route('/assign-duty', methods=['POST'])
def assign_duty():
    data = request.json
    officer_id = data['officer_id']
    date = datetime.strptime(data['date'], '%Y-%m-%d').date()
    shift_type = data['shift_type']
    # Smart allocation: check past duties to avoid consecutive nights
    recent_duties = Duty.query.filter_by(officer_id=officer_id).filter(Duty.date >= date.replace(day=1)).all()
    if shift_type == 'night' and any(d.shift_type == 'night' for d in recent_duties[-2:]):
        return jsonify({'success': False, 'message': 'Avoid consecutive night shifts'})
    duty = Duty(officer_id=officer_id, date=date, shift_type=shift_type)
    db.session.add(duty)
    db.session.commit()
    return jsonify({'success': True})

@app.route('/analytics', methods=['GET'])
def get_analytics():
    duties = Duty.query.all()
    shift_counts = {'day': 0, 'night': 0, 'emergency': 0}
    for d in duties:
        shift_counts[d.shift_type] += 1
    return jsonify(shift_counts)

@app.route('/mark-attendance', methods=['POST'])
def mark_attendance():
    data = request.json
    officer_id = data['officer_id']
    date = datetime.now().date()
    status = 'present'
    attendance = Attendance(officer_id=officer_id, date=date, status=status)
    db.session.add(attendance)
    db.session.commit()
    return jsonify({'success': True})

@app.route('/alerts/<int:officer_id>', methods=['GET'])
def get_alerts(officer_id):
    # Mock alerts
    alerts = ['New shift assigned for tomorrow', 'Emergency deployment at 10 PM']
    return jsonify(alerts)

@app.route('/add-officer', methods=['POST'])
def add_officer():
    data = request.json
    officer = Officer(name=data['name'], rank=data['rank'], availability=data.get('availability', ''))
    db.session.add(officer)
    db.session.commit()
    return jsonify({'success': True, 'id': officer.id})

@app.route('/edit-officer/<int:officer_id>', methods=['PUT'])
def edit_officer(officer_id):
    data = request.json
    officer = Officer.query.get(officer_id)
    if not officer:
        return jsonify({'success': False, 'message': 'Officer not found'}), 404
    officer.name = data.get('name', officer.name)
    officer.rank = data.get('rank', officer.rank)
    officer.availability = data.get('availability', officer.availability)
    db.session.commit()
    return jsonify({'success': True})

@app.route('/delete-officer/<int:officer_id>', methods=['DELETE'])
def delete_officer(officer_id):
    officer = Officer.query.get(officer_id)
    if not officer:
        return jsonify({'success': False, 'message': 'Officer not found'}), 404
    db.session.delete(officer)
    db.session.commit()
    return jsonify({'success': True})

@app.route('/attendance', methods=['GET'])
def get_all_attendance():
    attendance_records = Attendance.query.all()
    result = []
    for a in attendance_records:
        officer = Officer.query.get(a.officer_id)
        result.append({
            'id': a.id,
            'officer_id': a.officer_id,
            'officer_name': officer.name if officer else 'Unknown',
            'date': str(a.date),
            'status': a.status
        })
    return jsonify(result)

@app.route('/attendance/<int:officer_id>', methods=['GET'])
def get_officer_attendance(officer_id):
    attendance_records = Attendance.query.filter_by(officer_id=officer_id).all()
    return jsonify([{'date': str(a.date), 'status': a.status} for a in attendance_records])

@app.route('/schedule', methods=['GET'])
def get_schedule():
    duties = Duty.query.all()
    result = []
    for d in duties:
        officer = Officer.query.get(d.officer_id)
        result.append({
            'id': d.id,
            'officer_id': d.officer_id,
            'officer_name': officer.name if officer else 'Unknown',
            'date': str(d.date),
            'shift_type': d.shift_type,
            'status': d.status
        })
    return jsonify(result)

@app.route('/schedule-by-date/<date_str>', methods=['GET'])
def get_schedule_by_date(date_str):
    try:
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        duties = Duty.query.filter_by(date=target_date).all()
        result = []
        for d in duties:
            officer = Officer.query.get(d.officer_id)
            result.append({
                'id': d.id,
                'officer_id': d.officer_id,
                'officer_name': officer.name if officer else 'Unknown',
                'date': str(d.date),
                'shift_type': d.shift_type,
                'status': d.status
            })
        return jsonify(result)
    except:
        return jsonify({'error': 'Invalid date format'}), 400

@app.route('/chatbot', methods=['POST'])
def chatbot():
    data = request.json
    user_message = data.get('message', '').lower().strip()
    
    # AI Chatbot with intelligent responses
    responses = {
        'hello': 'Hello! Welcome to the Police Duty Roster System. How can I assist you today?',
        'hi': 'Hi there! How can I help you with duty scheduling or roster management?',
        'help': 'I can help you with:\n- Creating and managing schedules\n- Adding/editing officers\n- Tracking attendance\n- Viewing analytics\n- Duty allocation\n\nWhat would you like to do?',
        'schedule': 'To create a schedule, click "Create Schedule", select an officer, choose a date and shift type (Day/Night/Emergency), then click "Assign Duty".',
        'duty': 'I can help with duty assignments. Would you like to:\n1. Create a new duty\n2. View existing duties\n3. Get shift recommendations\nLet me know!',
        'officer': 'You can manage officers by:\n1. Click "Manage Officers"\n2. Add new officers with their rank\n3. Edit officer details\n4. Delete officers\nWhat would you like to do?',
        'attendance': 'To track attendance:\n1. Click "Monitor Attendance"\n2. View all officer attendance records\n3. See present/absent status\nWould you like to mark attendance?',
        'analytics': 'Analytics shows:\n- Duty distribution (Day/Night/Emergency shifts)\n- Attendance trends\n- Performance insights\nClick "View Analytics" to see charts!',
        'shift': 'Available shift types:\n- Day Shift: Regular daytime duty\n- Night Shift: Evening to morning duty\n- Emergency: Special alert deployment\nWhich shift would you like to assign?',
        'smart allocation': 'Our smart system prevents consecutive night shifts and balances workload fairly across all officers.',
        'alert': 'Officers receive alerts for:\n- New shift assignments\n- Emergency deployments\n- Schedule changes\nThis keeps the team informed in real-time!',
        'add officer': 'To add a new officer:\n1. Go to "Manage Officers"\n2. Click "Add New Officer"\n3. Enter name and rank\n4. Click "Add Officer"\nDone!',
        'edit officer': 'To edit an officer:\n1. Go to "Manage Officers"\n2. Click "Edit" next to the officer\n3. Enter new name/rank\n4. Confirm changes',
        'delete officer': 'To delete an officer:\n1. Go to "Manage Officers"\n2. Click "Delete" next to the officer\n3. Confirm deletion\nNote: Be careful as this action is permanent!',
        'dashboard': 'Your dashboard shows:\n- Quick access to all features\n- Officer and duty information\n- Schedule management\n- Attendance tracking\n- Performance analytics',
        'login': 'Login with your credentials:\n- Admin: username "admin", password "admin123"\n- Officer: username "officer", password "officer123"',
        'password': 'For security, please contact your administrator to change your password. Default credentials are provided during setup.',
        'report': 'Reports include:\n- Duty distribution analysis\n- Attendance records\n- Officer performance\n- Shift balance metrics',
        'features': 'Key features:\n✓ Smart Duty Allocation\n✓ Real-time Alerts\n✓ Officer Management\n✓ Attendance Tracking\n✓ Analytics & Reporting\n✓ Role-based Access',
    }
    
    # Check for exact matches
    if user_message in responses:
        return jsonify({'response': responses[user_message]})
    
    # Check for partial matches
    for key, value in responses.items():
        if key in user_message or user_message in key:
            return jsonify({'response': value})
    
    # Default response
    default_response = '''I'm here to help! I can assist with:
    
1. **Schedule Management** - Create and manage duty schedules
2. **Officer Management** - Add, edit, or remove officers
3. **Attendance Tracking** - Monitor officer attendance
4. **Analytics** - View duty distribution and insights
5. **Shift Allocation** - Smart duty assignment

What would you like help with? Try asking about:
- "schedule", "duty", "officer", "attendance", "analytics", "shift", "alert", "features", "help"'''
    
    return jsonify({'response': default_response})

@app.route('/')
def index():
    return send_from_directory('../frontend', 'index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('../frontend', path)

if __name__ == '__main__':
    app.run(debug=True)
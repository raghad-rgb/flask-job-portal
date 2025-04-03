from flask import Flask, request, render_template, flash, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField
from wtforms.validators import DataRequired


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'    # database config for connection
app.config['SECRET_KEY'] = 'mysecretkey'

db = SQLAlchemy(app)
migrate = Migrate(app, db)


# Models
class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200))
    employees_count = db.Column(db.Integer)
    
    jobs = db.relationship('Job', backref='company_data', lazy=True)

class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    company = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100))
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))

    def __repr__(self):
        return f"<Job {self.title}>"


class JobForm(FlaskForm):
    title = StringField('Job Title', validators=[DataRequired()])
    company = StringField('Company Name', validators=[DataRequired()])
    location = StringField('Location')
    submit = SubmitField()


class CompanyForm(FlaskForm):
    name = StringField('Company Name', validators=[DataRequired()])
    description = StringField('Description')
    employees_count = IntegerField('Employees Count')
    submit = SubmitField('Create Company')

# Routes
@app.route('/company/<int:company_id>')
def company_details(company_id):
    company = Company.query.get_or_404(company_id)
    return render_template('company_details.html', company=company)

@app.route('/jobs/create', methods=['GET', 'POST'])
def create():
    form = JobForm()
    form.submit.label.text = "Create Job"
    if form.validate_on_submit():
        title = form.title.data
        company = form.company.data
        location = form.location.data
        company_obj = Company.query.filter_by(name=company).first()

        if not company_obj:
            flash("Company not found. Please add it first.")
            return redirect(url_for('create'))

        new_job = Job(title=title, company=company, location=location, company_id=company_obj.id)
        db.session.add(new_job)
        db.session.commit()
        flash("Job created successfully!")
        return redirect(url_for('jobs'))

    return render_template('create_job.html', form=form)

@app.route('/company/create', methods=['GET', 'POST'])
def create_company():
    form = CompanyForm()

    if form.validate_on_submit():
        name = form.name.data
        description = form.description.data
        employees_count = form.employees_count.data

        company = Company(name=name, description=description, employees_count=employees_count)
        db.session.add(company)
        db.session.commit()

        flash("Company created successfully!")
        return redirect(url_for('company_details', company_id=company.id))

    return render_template('create_company.html', form=form)

@app.route('/jobs', methods=['GET'])
def jobs():
    jobs = Job.query.all()
    return render_template('jobs.html', jobs=jobs)

@app.route('/job/<int:job_id>', methods=['GET'])
def job_details(job_id):
    job = Job.query.get_or_404(job_id)
    return render_template('job_details.html', job=job)


@app.route('/job/update/<int:job_id>', methods=['GET', 'POST'])
def update_job_form(job_id):
    job = Job.query.get_or_404(job_id)
    form = JobForm(obj=job)
    form.submit.label.text = "Update Job"

    if form.validate_on_submit():
        job.title = form.title.data
        job.company = form.company.data
        job.location = form.location.data
        db.session.commit()
        flash("Job updated successfully!")
        return redirect(url_for('jobs'))

    return render_template('update_job.html', form=form, job=job)

@app.route('/job/delete/<int:job_id>', methods=['GET'])
def delete_job(job_id):
    job = Job.query.get_or_404(job_id)
    db.session.delete(job)
    db.session.commit()
    flash('Job deleted successfully!')
    return redirect(url_for('jobs'))
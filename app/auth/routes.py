"""Authentication routes."""

from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, current_app
from flask_login import login_user, logout_user, current_user, login_required
from urllib.parse import urlparse

from app import db
from app.auth import bp
from app.auth.forms import LoginForm, RegistrationForm, ResetPasswordRequestForm, ResetPasswordForm, ChangePasswordForm
from app.models import User, UserRole
from app.utils.security import generate_password_reset_token, verify_password_reset_token


@bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login page."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user is None or not user.check_password(form.password.data):
            flash('Invalid email or password', 'error')
            return redirect(url_for('auth.login'))
        
        if not user.is_active:
            flash('Your account has been deactivated. Please contact an administrator.', 'error')
            return redirect(url_for('auth.login'))
        
        # Update last login
        user.last_login_at = datetime.utcnow()
        db.session.commit()
        
        login_user(user, remember=form.remember_me.data)
        
        # Redirect to originally requested page or dashboard
        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            next_page = url_for('dashboard.index')
        
        flash(f'Welcome back, {user.full_name}!', 'success')
        return redirect(next_page)
    
    return render_template('auth/login.html', title='Sign In', form=form)


@bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration page."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            full_name=form.full_name.data,
            email=form.email.data,
            role=UserRole[form.role.data],
            is_active=True
        )
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', title='Register', form=form)


@bp.route('/logout')
@login_required
def logout():
    """User logout."""
    user_name = current_user.full_name
    logout_user()
    flash(f'You have been logged out successfully. Goodbye, {user_name}!', 'info')
    return redirect(url_for('auth.login'))


@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    """Request password reset."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user and user.is_active:
            token = generate_password_reset_token(user.id)
            
            # In a real application, you would send this token via email
            # For demo purposes, we'll log it and show a message
            current_app.logger.info(f'Password reset token for {user.email}: {token}')
            
            flash(f'Password reset instructions have been sent to {form.email.data}. '
                  f'(Demo: Check the application logs for the reset token)', 'info')
        else:
            # Don't reveal whether the email exists or not
            flash(f'Password reset instructions have been sent to {form.email.data}.', 'info')
        
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password_request.html', title='Reset Password', form=form)


@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Reset password with token."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    user_id = verify_password_reset_token(token)
    if not user_id:
        flash('The password reset link is invalid or has expired.', 'error')
        return redirect(url_for('auth.reset_password_request'))
    
    user = User.query.get(user_id)
    if not user or not user.is_active:
        flash('Invalid user or account is deactivated.', 'error')
        return redirect(url_for('auth.login'))
    
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        
        flash('Your password has been reset successfully. You can now log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password.html', title='Reset Password', form=form)


@bp.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Change current user's password."""
    form = ChangePasswordForm()
    
    if form.validate_on_submit():
        if not current_user.check_password(form.current_password.data):
            flash('Current password is incorrect.', 'error')
            return redirect(url_for('auth.change_password'))
        
        current_user.set_password(form.password.data)
        db.session.commit()
        
        flash('Your password has been changed successfully.', 'success')
        return redirect(url_for('dashboard.index'))
    
    return render_template('auth/change_password.html', title='Change Password', form=form)


@bp.route('/profile')
@login_required
def profile():
    """User profile page."""
    return render_template('auth/profile.html', title='Profile', user=current_user)
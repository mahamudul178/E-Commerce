





{% extends 'base.html' %}
{% load crispy_forms_tags %}

{% block title %}Register - ShopEase{% endblock %}

{% block content %}
<div class="container py-5">
    <div class="row justify-content-center">
        <div class="col-md-8 col-lg-6">
            <div class="card shadow">
                <div class="card-body p-5">
                    <div class="text-center mb-4">
                        <i class="fas fa-user-plus fa-3x text-primary mb-3"></i>
                        <h3>Create Account</h3>
                        <p class="text-muted">Join ShopEase today</p>
                    </div>
                    
                    <form method="post">
                        {% csrf_token %}
                        <div class="row">
                            <div class="col-md-6 mb-3">
                                <label for="{{ form.first_name.id_for_label }}" class="form-label">First Name</label>
                                {{ form.first_name }}
                            </div>
                            <div class="col-md-6 mb-3">
                                <label for="{{ form.last_name.id_for_label }}" class="form-label">Last Name</label>
                                {{ form.last_name }}
                            </div>
                        </div>
                        
                        <div class="mb-3">
                            <label for="{{ form.username.id_for_label }}" class="form-label">Username</label>
                            <div class="input-group">
                                <span class="input-group-text"><i class="fas fa-user"></i></span>
                                {{ form.username }}
                            </div>
                        </div>
                        
                        <div class="mb-3">
                            <label for="{{ form.email.id_for_label }}" class="form-label">Email</label>
                            <div class="input-group">
                                <span class="input-group-text"><i class="fas fa-envelope"></i></span>
                                {{ form.email }}
                            </div>
                        </div>
                        
                        <div class="mb-3">
                            <label for="{{ form.password1.id_for_label }}" class="form-label">Password</label>
                            <div class="input-group">
                                <span class="input-group-text"><i class="fas fa-lock"></i></span>
                                {{ form.password1 }}
                            </div>
                        </div>
                        
                        <div class="mb-3">
                            <label for="{{ form.password2.id_for_label }}" class="form-label">Confirm Password</label>
                            <div class="input-group">
                                <span class="input-group-text"><i class="fas fa-lock"></i></span>
                                {{ form.password2 }}
                            </div>
                        </div>
                        
                        <div class="mb-3 form-check">
                            <input type="checkbox" class="form-check-input" id="agreeTerms" required>
                            <label class="form-check-label" for="agreeTerms">
                                I agree to the <a href="#">Terms of Service</a> and <a href="#">Privacy Policy</a>
                            </label>
                        </div>
                        
                        <button type="submit" class="btn btn-primary w-100 mb-3">
                            <i class="fas fa-user-plus"></i> Create Account
                        </button>
                    </form>
                    
                    <hr class="my-4">
                    
                    <div class="text-center">
                        <p class="mb-0">Already have an account?</p>
                        <a href="{% url 'accounts:login' %}" class="btn btn-outline-primary w-100 mt-2">
                            <i class="fas fa-sign-in-alt"></i> Sign In
                        </a>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}








<!-- accounts/login.html
{% extends 'base.html' %}
{% load crispy_forms_tags %}

{% block title %}Login - ShopEase{% endblock %}

{% block content %}
<div class="container py-5">
    <div class="row justify-content-center">
        <div class="col-md-6 col-lg-4">
            <div class="card shadow">
                <div class="card-body p-5">
                    <div class="text-center mb-4">
                        <i class="fas fa-user-circle fa-3x text-primary mb-3"></i>
                        <h3>Welcome Back</h3>
                        <p class="text-muted">Sign in to your account</p>
                    </div>
                    
                    <form method="post" >
                        {% csrf_token %}
                        <div class="mb-3">
                            <label for="{{ form.username.id_for_label }}" class="form-label">Username</label>
                            <div class="input-group">
                                <span class="input-group-text"><i class="fas fa-user"></i></span>
                                {{ form.username }}
                            </div>
                        </div>
                        
                        <div class="mb-3">
                            <label for="{{ form.password.id_for_label }}" class="form-label">Password</label>
                            <div class="input-group">
                                <span class="input-group-text"><i class="fas fa-lock"></i></span>
                                {{ form.password }}
                            </div>
                        </div>
                        
                        <div class="mb-3 form-check">
                            <input type="checkbox" class="form-check-input" id="rememberMe">
                            <label class="form-check-label" for="rememberMe">Remember me</label>
                        </div>
                        
                        <button type="submit" class="btn btn-primary w-100 mb-3">
                            <i class="fas fa-sign-in-alt"></i> Sign In
                        </button>
                    </form>
                    
                    <div class="text-center">
                        <a href="{% url 'accounts:password_reset' %}" class="text-decoration-none">Forgot your password?</a>
                    </div>
                    
                    <hr class="my-4">
                    
                    <div class="text-center">
                        <p class="mb-0">Don't have an account?</p>
                        <a href="{% url 'accounts:register' %}" class="btn btn-outline-primary w-100 mt-2">
                            <i class="fas fa-user-plus"></i> Create Account
                        </a>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %} -->
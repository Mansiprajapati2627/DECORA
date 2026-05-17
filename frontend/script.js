// script.js - COMPLETE FIXED VERSION WITH WORKING LOGIN AND BOOKING

console.log("🎯 DECORA Events - Full JavaScript Loaded");

// ===== GLOBAL VARIABLES =====
let currentUser = null;
let userHasOrdered = false;

// ===== AUTHENTICATION FUNCTIONS =====

// Check login status on page load
async function checkAuthStatus() {
    try {
        console.log("🔍 Checking authentication status...");
        const response = await fetch('/api/check-auth', {
            credentials: 'include'
        });
        const data = await response.json();
        
        console.log("Auth check response:", data);
        
        if (data.logged_in) {
            currentUser = data.user;
            console.log("✅ User is logged in:", currentUser);
            updateUserInterface();
        } else {
            console.log("❌ User is not logged in");
        }
    } catch (error) {
        console.error('❌ Error checking auth status:', error);
    }
}

// Handle Login Form Submission 
function setupLoginForm() {
    const loginForm = document.getElementById("loginForm");
    if (!loginForm) {
        console.log("❌ Login form not found");
        return;
    }

    console.log("✅ Login form found, setting up event listener");

    // Remove HTML5 validation attributes to prevent browser validation
    const inputs = loginForm.querySelectorAll('input[required]');
    inputs.forEach(input => {
        input.removeAttribute('required');
    });

    // Remove any existing event listeners first
    const newLoginForm = loginForm.cloneNode(true);
    loginForm.parentNode.replaceChild(newLoginForm, loginForm);

    // Add fresh event listener to the new form
    newLoginForm.addEventListener("submit", async function(event) {
        event.preventDefault();
        event.stopPropagation();
        
        console.log("📝 Login form submitted - FORM IS WORKING!");
        
        const nameField = document.getElementById("nameField");
        const userName = document.getElementById("userName");
        const userEmail = document.getElementById("userEmail");
        const userPassword = document.getElementById("userPassword");
        const loginSubmit = document.getElementById("loginSubmit");

        console.log("Form elements found:", {
            nameField: !!nameField,
            userName: !!userName,
            userEmail: !!userEmail,
            userPassword: !!userPassword,
            loginSubmit: !!loginSubmit
        });

        // Show we're processing
        if (loginSubmit) {
            loginSubmit.textContent = "Processing...";
            loginSubmit.disabled = true;
        }

        try {
            // Manual validation instead of HTML5 validation
            if (!userEmail.value.trim()) {
                alert("❌ Please enter your email");
                if (loginSubmit) {
                    loginSubmit.textContent = nameField && nameField.style.display === "block" ? "Sign Up" : "Login";
                    loginSubmit.disabled = false;
                }
                return;
            }

            if (!userPassword.value.trim()) {
                alert("❌ Please enter your password");
                if (loginSubmit) {
                    loginSubmit.textContent = nameField && nameField.style.display === "block" ? "Sign Up" : "Login";
                    loginSubmit.disabled = false;
                }
                return;
            }

            console.log("Form values:", {
                isSignup: nameField && nameField.style.display === "block",
                email: userEmail.value,
                password: userPassword.value
            });

            if (nameField && nameField.style.display === "block") {
                // Sign up process
                console.log("👤 Attempting user registration");
                
                if (!userName.value.trim()) {
                    alert("❌ Please enter your full name");
                    if (loginSubmit) {
                        loginSubmit.textContent = "Sign Up";
                        loginSubmit.disabled = false;
                    }
                    return;
                }
                
                const response = await fetch('/api/register', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        full_name: userName.value,
                        email: userEmail.value,
                        password: userPassword.value
                    })
                });
                
                const data = await response.json();
                console.log("Registration response:", data);
                
                if (data.success) {
                    alert("✅ Account created successfully! Please login.");
                    toggleSignup(); // Switch back to login form
                } else {
                    alert("❌ " + (data.message || "Registration failed!"));
                }
            } else {
                // Login process
                console.log("🔐 Attempting user login");

                // Check for admin credentials first
                if ((userEmail.value === 'admin@decora.com' || userEmail.value === 'admin') && userPassword.value === 'admin123') {
                    console.log("👑 Admin login detected, redirecting to admin dashboard");
                    
                    // Redirect to admin dashboard immediately
                    alert("✅ Admin login successful! Redirecting to admin dashboard...");
                    closeLoginForm();
                    window.location.href = 'admin-dashboardfinal.html';
                    
                    // Reset form state
                    if (loginSubmit) {
                        loginSubmit.textContent = nameField && nameField.style.display === "block" ? "Sign Up" : "Login";
                        loginSubmit.disabled = false;
                    }
                    return; // Stop further execution
                }

                // Regular user login
                const response = await fetch('/api/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    credentials: 'include',
                    body: JSON.stringify({
                        email: userEmail.value,
                        password: userPassword.value
                    })
                });

                const data = await response.json();
                console.log("Login API response:", data);

                if (data.success) {
                    currentUser = data.user;
                    updateUserInterface();
                    alert("✅ Login successful!");
                    closeLoginForm();
                    
                    // Dispatch event for other pages
                    window.dispatchEvent(new Event('userLoggedIn'));
                } else {
                    alert("❌ " + (data.message || "Login failed!"));
                }
            }
            
            // Reset form state
            if (loginSubmit) {
                loginSubmit.textContent = nameField && nameField.style.display === "block" ? "Sign Up" : "Login";
                loginSubmit.disabled = false;
            }
            
        } catch (error) {
            console.error('💥 Error during authentication:', error);
            alert("❌ An error occurred. Please try again.");
            
            // Reset button state on error
            if (loginSubmit) {
                loginSubmit.textContent = nameField && nameField.style.display === "block" ? "Sign Up" : "Login";
                loginSubmit.disabled = false;
            }
        }
    });

    console.log("✅ Login form event listener setup complete");
}

// Logout function
async function logout() {
    try {
        console.log("🚪 Attempting logout");
        const response = await fetch('/api/logout', {
            method: 'POST',
            credentials: 'include'
        });
        
        const data = await response.json();
        console.log("Logout response:", data);
        
        if (data.success) {
            currentUser = null;
            userHasOrdered = false;
            updateUserInterface();
            alert("👋 You have been logged out.");
            
            // Dispatch event for other pages
            window.dispatchEvent(new Event('userLoggedOut'));
        }
    } catch (error) {
        console.error('❌ Error logging out:', error);
    }
}
            

// Update UI based on user state
function updateUserInterface() {
    console.log("🎨 Updating user interface");
    
    const userSection = document.getElementById("userSection");
    const customizeLink = document.getElementById("customizeLink");
    const addReviewCard = document.getElementById("addReviewCard");
    const bookingLink = document.getElementById("bookingLink");
    
    if (currentUser) {
        // User is logged in
        console.log("🔄 Setting logged-in UI state");
        userSection.innerHTML = `
            <div class="user-info">
                <i class="fas fa-user-circle"></i>
                <span>${currentUser.name}</span>
                <button class="login-btn" onclick="logout()" style="margin-left:10px; cursor: pointer;">Logout</button>
            </div>
        `;
        
        // Show customization link
        if (customizeLink) {
            customizeLink.style.display = "block";
            console.log("✅ Customization link shown");
        }
        
        // Show booking link
        if (bookingLink) {
            bookingLink.style.display = "block";
            console.log("✅ Booking link shown");
        }
        
        // Show add review card for logged in users
        if (addReviewCard) {
            addReviewCard.style.display = "flex";
            console.log("✅ Add review card shown");
        }
    } else {
        // User is not logged in
        console.log("🔄 Setting logged-out UI state");
        userSection.innerHTML = `
            <button class="login-btn" onclick="openLoginForm()" style="cursor: pointer;">Login / Sign Up</button>
        `;
        
        // Hide customization link
        if (customizeLink) {
            customizeLink.style.display = "none";
            console.log("❌ Customization link hidden");
        }
        
        // Hide booking link
        if (bookingLink) {
            bookingLink.style.display = "none";
            console.log("❌ Booking link hidden");
        }
        
        // Hide add review card for non-logged in users
        if (addReviewCard) {
            addReviewCard.style.display = "none";
            console.log("❌ Add review card hidden");
        }
    }
}

// ===== BOOKING FUNCTIONALITY =====

// Handle booking form submission - FIXED VERSION
function setupBookingForm() {
    const bookingForm = document.getElementById("bookingForm");
    if (!bookingForm) {
        console.log("ℹ️ Booking form not found on this page");
        return;
    }

    console.log("✅ Booking form found, setting up event listener");

    // Remove HTML5 validation attributes
    const inputs = bookingForm.querySelectorAll('input[required], select[required]');
    inputs.forEach(input => {
        input.removeAttribute('required');
    });

    // Remove any existing event listeners first
    const newBookingForm = bookingForm.cloneNode(true);
    bookingForm.parentNode.replaceChild(newBookingForm, bookingForm);

    // Add fresh event listener to the new form
    newBookingForm.addEventListener("submit", async function(event) {
        event.preventDefault();
        event.stopPropagation();
        
        console.log("📅 Booking form submitted - FORM IS WORKING!");

        // Check if user is logged in
        if (!currentUser) {
            alert("🔒 Please login to book an event.");
            openLoginForm();
            return;
        }

        const eventType = document.getElementById("event");
        const eventDate = document.getElementById("date");
        const eventTime = document.getElementById("time");
        const guestCount = document.getElementById("guest_count");
        const venue = document.getElementById("venue");
        const specialRequests = document.getElementById("special_requests");
        const submitButton = this.querySelector('button[type="submit"]');

        console.log("Booking form elements found:", {
            eventType: !!eventType,
            eventDate: !!eventDate,
            eventTime: !!eventTime,
            guestCount: !!guestCount,
            venue: !!venue,
            specialRequests: !!specialRequests,
            submitButton: !!submitButton
        });

        // Show we're processing
        if (submitButton) {
            submitButton.textContent = "Processing...";
            submitButton.disabled = true;
        }

        try {
            // Manual validation
            if (!eventType || !eventType.value) {
                alert("❌ Please select an event type");
                resetSubmitButton(submitButton);
                return;
            }

            if (!eventDate || !eventDate.value) {
                alert("❌ Please select a date");
                resetSubmitButton(submitButton);
                return;
            }

            if (!eventTime || !eventTime.value) {
                alert("❌ Please select a time");
                resetSubmitButton(submitButton);
                return;
            }

            const bookingData = {
                event_type: eventType.value,
                event_date: eventDate.value,
                event_time: eventTime.value,
                guest_count: guestCount?.value || 50,
                venue: venue?.value || "Customer Venue",
                special_requests: specialRequests?.value || ""
            };

            console.log("Booking data:", bookingData);

            const response = await fetch('/api/bookings', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
                body: JSON.stringify(bookingData)
            });
            
            const data = await response.json();
            console.log("Booking response:", data);
            
            if (data.success) {
                userHasOrdered = true;
                alert(`🎉 Booking Confirmed!\n\nEvent: ${bookingData.event_type}\nDate: ${bookingData.event_date}\nTime: ${bookingData.event_time}\n\nThank you for choosing DECORA!`);
                this.reset();
                updateUserInterface();
                
                // Redirect to home page after successful booking
                setTimeout(() => {
                    window.location.href = 'index.html';
                }, 2000);
            } else {
                alert("❌ " + (data.message || "Booking failed!"));
            }
        } catch (error) {
            console.error('💥 Error creating booking:', error);
            alert("❌ An error occurred. Please try again.");
        } finally {
            // Reset button state
            resetSubmitButton(submitButton);
        }
    });

    console.log("✅ Booking form event listener setup complete");
}

// Helper function to reset submit button
function resetSubmitButton(button) {
    if (button) {
        button.textContent = "Book Now";
        button.disabled = false;
    }
}



// ===== CUSTOMIZATION FUNCTIONALITY =====
function setupCustomizationForm() {
    const customizationForm = document.getElementById("customizationForm");
    if (!customizationForm) {
        console.log("ℹ️ Customization form not found on this page");
        return;
    }

    console.log("✅ Customization form found, setting up event listener");

    // Remove any existing event listeners first
    const newCustomizationForm = customizationForm.cloneNode(true);
    customizationForm.parentNode.replaceChild(newCustomizationForm, customizationForm);

    newCustomizationForm.addEventListener("submit", async function(event) {
        event.preventDefault();
        event.stopPropagation();
        console.log("🎨 Customization form submitted");

        // Check if user is logged in
        if (!currentUser) {
            alert("🔒 Please login to submit customization requests.");
            openLoginForm();
            return;
        }

        const submitButton = this.querySelector('button[type="submit"]');
        
        // Show processing
        if (submitButton) {
            submitButton.textContent = "Processing...";
            submitButton.disabled = true;
        }

        try {
            // Get form values
            const customEventType = document.getElementById("customEventType").value;
            const customDate = document.getElementById("customDate").value;
            const customTime = document.getElementById("customTime").value;
            const customDescription = document.getElementById("customDescription").value;

            // Manual validation
            if (!customEventType) {
                alert("❌ Please select an event type");
                resetSubmitButton(submitButton);
                return;
            }

            if (!customDate) {
                alert("❌ Please select a date");
                resetSubmitButton(submitButton);
                return;
            }

            if (!customTime) {
                alert("❌ Please select a time");
                resetSubmitButton(submitButton);
                return;
            }

            if (!customDescription.trim()) {
                alert("❌ Please provide a description of your customization request");
                resetSubmitButton(submitButton);
                return;
            }

            // Prepare data for backend - using field names that match backend expectations
            const customizationData = {
                customName: currentUser.name, // Use logged-in user's name
                customEventType: customEventType,
                customDate: customDate,
                customTime: customTime,
                customDescription: customDescription
            };

            console.log("📤 Sending customization data:", customizationData);

            const response = await fetch('/api/customizations', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
                body: JSON.stringify(customizationData)
            });
            
            const data = await response.json();
            console.log("📥 Customization response:", data);
            
            if (data.success) {
                alert("✅ Thank you! We will get in touch with you soon to discuss your customization request.");
                this.reset();
                closeCustomizationForm();
            } else {
                alert("❌ " + (data.message || "Submission failed!"));
            }
        } catch (error) {
            console.error('💥 Error submitting customization:', error);
            alert("❌ An error occurred. Please try again.");
        } finally {
            // Reset button state
            if (submitButton) {
                submitButton.textContent = "Submit";
                submitButton.disabled = false;
            }
        }
    });
}

// ===== REVIEW FUNCTIONALITY =====

function setupReviewForm() {
    const reviewForm = document.getElementById("reviewForm");
    if (!reviewForm) {
        console.log("ℹ️ Review form not found on this page");
        return;
    }

    console.log("✅ Review form found, setting up event listener");

    // Remove any existing event listeners first
    const newReviewForm = reviewForm.cloneNode(true);
    reviewForm.parentNode.replaceChild(newReviewForm, reviewForm);

    newReviewForm.addEventListener("submit", async function(event) {
        event.preventDefault();
        event.stopPropagation();
        console.log("⭐ Review form submitted");

        // Check if user is logged in
        if (!currentUser) {
            alert("🔒 Please login to submit a review.");
            openLoginForm();
            return;
        }

        const submitButton = this.querySelector('button[type="submit"]');
        
        // Show processing
        if (submitButton) {
            submitButton.textContent = "Processing...";
            submitButton.disabled = true;
        }

        const ratingMap = {
            '⭐': 1,
            '⭐⭐': 2,
            '⭐⭐⭐': 3,
            '⭐⭐⭐⭐': 4,
            '⭐⭐⭐⭐⭐': 5
        };
         const reviewData = {
    reviewname: currentUser.name, // This will use the logged-in user's name
    rating: ratingMap[document.getElementById("rating").value],
    review: document.getElementById("review").value
};

        try {
            const response = await fetch('/api/reviews', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
                body: JSON.stringify(reviewData)
            });
            
            const data = await response.json();
            console.log("Review response:", data);
            
            if (data.success) {
                alert("✅ Thank you for your review!");
                this.reset();
                closeReviewForm();
            } else {
                alert("❌ " + (data.message || "Review submission failed!"));
            }
        } catch (error) {
            console.error('💥 Error submitting review:', error);
            alert("❌ An error occurred. Please try again.");
        } finally {
            // Reset button state
            if (submitButton) {
                submitButton.textContent = "Submit Review";
                submitButton.disabled = false;
            }
        }
    });
}

// ===== UI CONTROL FUNCTIONS =====

// Navigation Menu Toggle
function toggleMenu() {
    const navMenu = document.getElementById("navMenu");
    if (navMenu) {
        navMenu.classList.toggle("active");
        console.log("🍔 Mobile menu toggled");
    }
}

// Login/Signup Modal Functions - FIXED VERSION
function openLoginForm() {
    console.log("🔓 Opening login form");
    const loginModal = document.getElementById("loginModal");
    if (loginModal) {
        loginModal.style.display = "flex";
        document.body.style.overflow = "hidden";
        console.log("✅ Login modal displayed");
        
        // Clear any previous inputs
        const userEmail = document.getElementById('userEmail');
        const userPassword = document.getElementById('userPassword');
        const userName = document.getElementById('userName');
        
        if (userEmail) userEmail.value = '';
        if (userPassword) userPassword.value = '';
        if (userName) userName.value = '';
        
        // Focus on email field
        setTimeout(() => {
            if (userEmail) userEmail.focus();
        }, 100);
    } else {
        console.log("❌ Login modal not found");
    }
}

function closeLoginForm() {
    const loginModal = document.getElementById("loginModal");
    if (loginModal) {
        loginModal.style.display = "none";
        document.body.style.overflow = "auto";
        console.log("🔒 Login modal closed");
    }
}

function toggleSignup() {
    console.log("🔄 Toggling signup/login mode");
    const nameField = document.getElementById("nameField");
    const loginTitle = document.getElementById("loginTitle");
    const loginSubmit = document.getElementById("loginSubmit");
    const toggleText = document.getElementById("toggleText");
    
    if (!nameField || !loginTitle || !loginSubmit || !toggleText) {
        console.log("❌ Toggle elements not found");
        return;
    }
    
    if (nameField.style.display === "none" || nameField.style.display === "") {
        // Switch to signup
        nameField.style.display = "block";
        loginTitle.textContent = "Sign Up";
        loginSubmit.textContent = "Sign Up";
        toggleText.innerHTML = 'Already have an account? <a href="#" onclick="toggleSignup(); return false;">Login</a>';
        console.log("✅ Switched to Sign Up mode");
    } else {
        // Switch to login
        nameField.style.display = "none";
        loginTitle.textContent = "Login";
        loginSubmit.textContent = "Login";
        toggleText.innerHTML = 'Don\'t have an account? <a href="#" onclick="toggleSignup(); return false;">Sign up</a>';
        console.log("✅ Switched to Login mode");
    }
}

// Customization Modal Functions
function openCustomizationForm() {
    console.log("🎨 Opening customization form");
    if (!currentUser) {
        alert("🔒 Please login to access customization options.");
        openLoginForm();
        return;
    }
    const customizationModal = document.getElementById("customizationModal");
    if (customizationModal) {
        customizationModal.style.display = "flex";
        document.body.style.overflow = "hidden";
        console.log("✅ Customization modal displayed");
    }
}

function closeCustomizationForm() {
    const customizationModal = document.getElementById("customizationModal");
    if (customizationModal) {
        customizationModal.style.display = "none";
        document.body.style.overflow = "auto";
        console.log("🔒 Customization modal closed");
    }
}

// Review Modal Functions
function openReviewForm() {
    console.log("⭐ Opening review form");
    if (!currentUser) {
        alert("🔒 Please login to add a review.");
        openLoginForm();
        return;
    }
    const reviewModal = document.getElementById("reviewModal");
    if (reviewModal) {
        reviewModal.style.display = "flex";
        document.body.style.overflow = "hidden";
        console.log("✅ Review modal displayed");
    }
}

function closeReviewForm() {
    const reviewModal = document.getElementById("reviewModal");
    if (reviewModal) {
        reviewModal.style.display = "none";
        document.body.style.overflow = "auto";
        console.log("🔒 Review modal closed");
    }
}

// Close modals when clicking outside
window.onclick = function(event) {
    const reviewModal = document.getElementById("reviewModal");
    const customizationModal = document.getElementById("customizationModal");
    const loginModal = document.getElementById("loginModal");
    
    if (event.target === reviewModal) {
        closeReviewForm();
        console.log("🔒 Review modal closed (outside click)");
    }
    if (event.target === customizationModal) {
        closeCustomizationForm();
        console.log("🔒 Customization modal closed (outside click)");
    }
    if (event.target === loginModal) {
        closeLoginForm();
        console.log("🔒 Login modal closed (outside click)");
    }
}

// Close modal with Escape key
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        closeLoginForm();
        closeReviewForm();
        closeCustomizationForm();
    }
});

// FAQ Toggle Functionality
function setupFAQ() {
    const faqQuestions = document.querySelectorAll(".faq-question");
    if (faqQuestions.length > 0) {
        console.log("❓ Setting up FAQ functionality");
        faqQuestions.forEach(question => {
            question.addEventListener("click", () => {
                question.classList.toggle("active");
                const answer = question.nextElementSibling;
                
                if (answer.style.maxHeight) {
                    answer.style.maxHeight = null;
                    console.log("📖 FAQ answer closed");
                } else {
                    answer.style.maxHeight = answer.scrollHeight + "px";
                    console.log("📖 FAQ answer opened");
                }
            });
        });
    }
}

// ===== EVENT LISTENERS FOR NAVIGATION =====
function setupNavigation() {
    console.log("🧭 Setting up navigation event listeners");
    
    // Setup navigation login button
    const navLoginBtn = document.querySelector('.user-actions .login-btn');
    if (navLoginBtn) {
        // Remove any existing event listeners
        const newNavLoginBtn = navLoginBtn.cloneNode(true);
        navLoginBtn.parentNode.replaceChild(newNavLoginBtn, navLoginBtn);
        
        // Add fresh event listener
        newNavLoginBtn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            console.log("🎯 Navigation login button clicked");
            openLoginForm();
        });
        console.log("✅ Navigation login button listener added");
    } else {
        console.log("❌ Navigation login button not found");
    }
    
    // Setup mobile menu toggle
    const hamburger = document.querySelector('.hamburger');
    if (hamburger) {
        hamburger.addEventListener('click', toggleMenu);
        console.log("✅ Hamburger menu listener added");
    }
    
    // Setup all modal close buttons
    setupModalCloseButtons();
}

// Setup modal close buttons
function setupModalCloseButtons() {
    const closeButtons = document.querySelectorAll('.close');
    closeButtons.forEach(button => {
        button.addEventListener('click', function() {
            const modal = this.closest('.modal');
            if (modal) {
                modal.style.display = 'none';
                document.body.style.overflow = 'auto';
            }
        });
    });
}

// ===== GLOBAL EVENT LISTENERS =====
function setupGlobalEventListeners() {
    console.log("🌐 Setting up global event listeners");
    
    // Listen for login events from other pages
    window.addEventListener('userLoggedIn', function() {
        console.log("🔄 User logged in event received");
        checkAuthStatus();
    });
    
    // Listen for logout events from other pages
    window.addEventListener('userLoggedOut', function() {
        console.log("🔄 User logged out event received");
        currentUser = null;
        updateUserInterface();
    });
}

// ===== INITIALIZATION =====
document.addEventListener('DOMContentLoaded', function() {
    console.log("🚀 DOM fully loaded - Initializing DECORA Events");
    
    // Setup all functionality
    setupNavigation();
    setupLoginForm();
    setupBookingForm();
    setupCustomizationForm();
    setupReviewForm();
    setupFAQ();
    setupGlobalEventListeners();
    
    // Check if user is already logged in
    checkAuthStatus();
    
    console.log("✅ DECORA Events initialization complete");
});
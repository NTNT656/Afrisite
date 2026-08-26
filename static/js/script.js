// African Frame — JavaScript

document.addEventListener('DOMContentLoaded', function() {

    // ================================================================
    // MOBILE MENU TOGGLE
    // ================================================================
    var toggle = document.getElementById('mobileToggle');
    var mobileNav = document.getElementById('mobileNav');

    if (toggle && mobileNav) {
        toggle.addEventListener('click', function(e) {
            e.stopPropagation();
            mobileNav.classList.toggle('open');
        });

        document.addEventListener('click', function(e) {
            if (mobileNav.classList.contains('open')) {
                var isClickInside = mobileNav.contains(e.target) || toggle.contains(e.target);
                if (!isClickInside) {
                    mobileNav.classList.remove('open');
                }
            }
        });

        var mobileLinks = mobileNav.querySelectorAll('a');
        for (var i = 0; i < mobileLinks.length; i++) {
            mobileLinks[i].addEventListener('click', function() {
                mobileNav.classList.remove('open');
            });
        }
    }

    // ================================================================
    // ACTIVE NAV LINK
    // ================================================================
    var currentPath = window.location.pathname;
    var navLinks = document.querySelectorAll('nav.links a, .mobile-nav a');

    for (var i = 0; i < navLinks.length; i++) {
        var link = navLinks[i];
        var href = link.getAttribute('href');

        if (href && href !== '#' && href !== '/') {
            if (currentPath === href || (currentPath + '/') === href) {
                link.classList.add('active');
            }
        } else if (href === '/' && currentPath === '/') {
            link.classList.add('active');
        }
    }

    // ================================================================
    // AUTOCOMPLETE – UNIVERSAL (works on all pages with #searchInput)
    // ================================================================
    var autoInput = document.getElementById('searchInput');
    var autoList = document.getElementById('autocompleteList');

    if (autoInput && autoList) {
        var debounceTimer;

        autoInput.addEventListener('input', function() {
            var query = this.value.trim();
            clearTimeout(debounceTimer);

            if (query.length < 2) {
                autoList.style.display = 'none';
                return;
            }

            debounceTimer = setTimeout(function() {
                fetch('/api/autocomplete?q=' + encodeURIComponent(query))
                    .then(function(res) { return res.json(); })
                    .then(function(data) {
                        if (data.length === 0) {
                            autoList.style.display = 'none';
                            return;
                        }
                        var html = '';
                        data.forEach(function(item) {
                            var year = item.year ? ' (' + item.year + ')' : '';
                            var typeLabel = item.type === 'movie' ? '🎬' : item.type === 'tv' ? '📺' : '👤';
                            html += '<div class="autocomplete-item" data-label="' + item.label + '" style="padding:8px 16px;cursor:pointer;border-bottom:1px solid #eee;display:flex;align-items:center;gap:8px;">';
                            html += '<span>' + typeLabel + '</span>';
                            html += '<span><strong>' + item.label + '</strong>' + year + '</span>';
                            html += '</div>';
                        });
                        autoList.innerHTML = html;
                        autoList.style.display = 'block';

                        var items = autoList.querySelectorAll('.autocomplete-item');
                        items.forEach(function(el) {
                            el.addEventListener('click', function() {
                                autoInput.value = this.dataset.label;
                                autoList.style.display = 'none';
                                var form = autoInput.closest('form');
                                if (form) form.submit();
                            });
                        });
                    })
                    .catch(function() {
                        autoList.style.display = 'none';
                    });
            }, 300);
        });

        document.addEventListener('click', function(e) {
            if (!autoInput.contains(e.target) && !autoList.contains(e.target)) {
                autoList.style.display = 'none';
            }
        });

        var form = autoInput.closest('form');
        if (form) {
            form.addEventListener('submit', function() {
                autoList.style.display = 'none';
            });
        }
    }

    // ================================================================
    // COOKIE CONSENT
    // ================================================================
    (function() {
        var consentBanner = document.getElementById('cookieConsent');
        var acceptBtn = document.getElementById('cookieAccept');
        var declineBtn = document.getElementById('cookieDecline');

        function setCookieConsent(accepted) {
            var expiry = new Date();
            expiry.setFullYear(expiry.getFullYear() + 1);
            document.cookie = 'cookie_consent=' + (accepted ? 'accepted' : 'declined') + '; expires=' + expiry.toUTCString() + '; path=/';
            consentBanner.style.display = 'none';
        }

        function checkCookieConsent() {
            var match = document.cookie.match(/cookie_consent=([^;]+)/);
            if (match) {
                consentBanner.style.display = 'none';
                return;
            }
            consentBanner.style.display = 'flex';
        }

        if (consentBanner && acceptBtn && declineBtn) {
            acceptBtn.addEventListener('click', function() {
                setCookieConsent(true);
            });
            declineBtn.addEventListener('click', function() {
                setCookieConsent(false);
            });
            checkCookieConsent();
        }
    })();

});
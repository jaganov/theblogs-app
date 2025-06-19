document.addEventListener('DOMContentLoaded', function() {
    // Mobile menu toggle
    const navbarToggle = document.querySelector('.navbar-toggle');
    const navbarMenu = document.querySelector('.navbar-menu');

    if (navbarToggle && navbarMenu) {
        navbarToggle.addEventListener('click', function() {
            navbarMenu.classList.toggle('active');
        });
    }

    // Calendar functionality
    const calendarDropdown = document.getElementById('calendarDropdown');
    const calendarDays = document.querySelector('.calendar-days');
    const calendarTitle = document.querySelector('.calendar-title');
    const prevButton = document.querySelector('.calendar-nav.prev');
    const nextButton = document.querySelector('.calendar-nav.next');

    let currentDate = new Date();
    let currentMonth = currentDate.getMonth();
    let currentYear = currentDate.getFullYear();
    let daysWithPosts = new Set();

    async function fetchDaysWithPosts(year, month) {
        try {
            const response = await fetch(`/api/days-with-posts/?year=${year}&month=${month + 1}`);
            if (response.ok) {
                const data = await response.json();
                daysWithPosts = new Set(data.days);
                updateCalendar();
            }
        } catch (error) {
            console.error('Error fetching days with posts:', error);
        }
    }

    function updateCalendar() {
        const firstDay = new Date(currentYear, currentMonth, 1);
        const lastDay = new Date(currentYear, currentMonth + 1, 0);
        const startingDay = firstDay.getDay();
        const totalDays = lastDay.getDate();

        calendarTitle.textContent = `${firstDay.toLocaleString('default', { month: 'long' })} ${currentYear}`;
        
        let daysHTML = '';
        
        // Add empty cells for days before the first day of the month
        for (let i = 0; i < startingDay; i++) {
            daysHTML += '<div class="calendar-day"></div>';
        }

        // Add days of the month
        for (let day = 1; day <= totalDays; day++) {
            const isToday = day === currentDate.getDate() && 
                          currentMonth === currentDate.getMonth() && 
                          currentYear === currentDate.getFullYear();
            const hasPosts = daysWithPosts.has(day);
            
            daysHTML += `
                <div class="calendar-day ${isToday ? 'active' : ''} ${hasPosts ? 'has-posts' : ''}" 
                     data-date="${currentYear}-${String(currentMonth + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}">
                    ${day}
                </div>
            `;
        }

        calendarDays.innerHTML = daysHTML;
    }

    if (calendarDropdown && calendarDays) {
        // Initialize calendar
        fetchDaysWithPosts(currentYear, currentMonth);

        // Handle month navigation
        if (prevButton && nextButton) {
            prevButton.addEventListener('click', function(e) {
                e.preventDefault();
                currentMonth--;
                if (currentMonth < 0) {
                    currentMonth = 11;
                    currentYear--;
                }
                fetchDaysWithPosts(currentYear, currentMonth);
            });

            nextButton.addEventListener('click', function(e) {
                e.preventDefault();
                currentMonth++;
                if (currentMonth > 11) {
                    currentMonth = 0;
                    currentYear++;
                }
                fetchDaysWithPosts(currentYear, currentMonth);
            });
        }

        // Handle day clicks
        calendarDays.addEventListener('click', function(e) {
            const day = e.target;
            if (day.classList.contains('calendar-day') && day.textContent.trim()) {
                // Remove active class from all days
                document.querySelectorAll('.calendar-day').forEach(d => d.classList.remove('active'));
                // Add active class to clicked day
                day.classList.add('active');
                
                // Get the selected date and redirect to search page
                const selectedDate = day.dataset.date;
                window.location.href = `/search/?date=${selectedDate}`;
            }
        });
    }
}); 
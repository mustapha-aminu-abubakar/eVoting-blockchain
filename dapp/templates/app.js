document.addEventListener('DOMContentLoaded', function () {
  // ===== Signup page logic =====
  (function initSignup() {
    const form = document.getElementById('signupForm');
    if (!form) return;
    const inputs = {
      fullName: document.getElementById('fullName'),
      email: document.getElementById('email'),
      password: document.getElementById('password'),
      confirmPassword: document.getElementById('confirmPassword')
    };
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      const formData = {
        fullName: inputs.fullName.value.trim(),
        email: inputs.email.value.trim(),
        password: inputs.password.value,
        confirmPassword: inputs.confirmPassword.value
      };
      if (formData.password.length < 8) {
        alert('Password must be at least 8 characters.');
        return;
      }
      if (formData.password !== formData.confirmPassword) {
        alert('Passwords do not match.');
        return;
      }
      console.log('Form submitted:', formData);
      alert('Form submitted. Check console for data.');
    });
  })();

  // ===== Signin page logic =====
  (function initSignin() {
    const form = document.getElementById('signinForm');
    if (!form) return;
    const emailInput = document.getElementById('email');
    const passwordInput = document.getElementById('password');
    const rememberMeInput = document.getElementById('rememberMe');
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      const formData = {
        email: emailInput.value.trim(),
        password: passwordInput.value,
        rememberMe: !!rememberMeInput.checked
      };
      console.log('Sign in data:', formData);
      alert('Sign in submitted. Check console for data.');
    });
  })();

  // ===== Aspirant page logic =====
  (function initAspirant() {
    const aspirantsPage = document.getElementById('aspirantsPage');
    const detailsPage = document.getElementById('candidateDetailsPage');
    if (!aspirantsPage && !detailsPage) return;

    // Mobile menu controls (list view)
    const mobileMenuToggle = document.getElementById('mobileMenuToggle');
    const menuIcon = document.getElementById('menuIcon');
    const closeIcon = document.getElementById('closeIcon');
    const mobileNav = document.getElementById('mobileNav');

    // Mobile menu controls (details view)
    const mobileMenuToggleDetails = document.getElementById('mobileMenuToggleDetails');
    const menuIconDetails = document.getElementById('menuIconDetails');
    const closeIconDetails = document.getElementById('closeIconDetails');
    const mobileNavDetails = document.getElementById('mobileNavDetails');

    if (mobileMenuToggle && mobileNav && menuIcon && closeIcon) {
      mobileMenuToggle.addEventListener('click', () => {
        const hidden = mobileNav.classList.contains('hidden');
        mobileNav.classList.toggle('hidden');
        if (hidden) {
          menuIcon.classList.add('hidden');
          closeIcon.classList.remove('hidden');
        } else {
          menuIcon.classList.remove('hidden');
          closeIcon.classList.add('hidden');
        }
      });
    }

    if (mobileMenuToggleDetails && mobileNavDetails && menuIconDetails && closeIconDetails) {
      mobileMenuToggleDetails.addEventListener('click', () => {
        const hidden = mobileNavDetails.classList.contains('hidden');
        mobileNavDetails.classList.toggle('hidden');
        if (hidden) {
          menuIconDetails.classList.add('hidden');
          closeIconDetails.classList.remove('hidden');
        } else {
          menuIconDetails.classList.remove('hidden');
          closeIconDetails.classList.add('hidden');
        }
      });
    }

    const categoryButton = document.getElementById('categoryButton');
    const categoryDropdown = document.getElementById('categoryDropdown');
    const currentCategoryLabel = document.getElementById('currentCategoryLabel');
    const chevronIcon = document.getElementById('chevronIcon');
    const candidatesList = document.getElementById('candidatesList');

    const detailImage = document.getElementById('detailImage');
    const detailName = document.getElementById('detailName');
    const detailKey = document.getElementById('detailKey');
    const backButton = document.getElementById('backButton');
    const confirmButton = document.getElementById('confirmButton');

    const candidatesData = {
      hod: [
        { id: 1, name: 'Mustapha Aminu', party: 'COEN PARTY', image: '/images/candidate1.jpeg', publicKey: 'Euqw12jskaOjSdF' },
        { id: 2, name: 'Raji Abdulfatai Ridwan', party: 'CVEN PARTY', image: '/images/candidate2.jpeg', publicKey: 'Bxqp98mklaPqWer' },
        { id: 3, name: 'Dr. Sarah Johnson', party: 'TECH PARTY', image: '/images/candidate3.jpeg', publicKey: 'Cytr45nopbRtYui' }
      ],
      examOfficer: [
        { id: 4, name: 'Ahmed Bello', party: 'ACADEMIC PARTY', image: '/images/exam1.jpeg', publicKey: 'Dxyw67qrsaLmNop' },
        { id: 5, name: 'Fatima Hassan', party: 'PROGRESS PARTY', image: '/images/exam2.jpeg', publicKey: 'Ezab89tuvbQwErt' }
      ],
      secretary: [
        { id: 6, name: 'Kemi Adebayo', party: 'UNITY PARTY', image: '/images/secretary1.jpeg', publicKey: 'Fhgc12defcZxCvb' },
        { id: 7, name: 'Ibrahim Yusuf', party: 'FORWARD PARTY', image: '/images/secretary2.jpeg', publicKey: 'Gjkl34ghijAsQwe' }
      ]
    };

    const categories = [
      { id: 'hod', label: 'HOD ASPIRANTS' },
      { id: 'examOfficer', label: 'EXAM OFFICER ASPIRANTS' },
      { id: 'secretary', label: 'SECRETARY ASPIRANTS' }
    ];

    let selectedCategory = 'hod';
    let selectedCandidate = null;

    function toggleDropdown() {
      if (!categoryDropdown) return;
      const isHidden = categoryDropdown.classList.contains('hidden');
      categoryDropdown.classList.toggle('hidden');
      if (chevronIcon) chevronIcon.classList.toggle('rotate-180', isHidden);
    }

    function closeDropdown() {
      if (!categoryDropdown || !chevronIcon) return;
      categoryDropdown.classList.add('hidden');
      chevronIcon.classList.remove('rotate-180');
    }

    function renderCategoryOptions() {
      if (!categoryDropdown) return;
      categoryDropdown.innerHTML = '';
      categories.forEach((category) => {
        const button = document.createElement('button');
        button.className = 'w-full px-6 py-3 text-left hover:bg-gray-100 transition-colors border-b border-gray-200 last:border-b-0';
        button.textContent = category.label;
        button.addEventListener('click', () => {
          selectedCategory = category.id;
          if (currentCategoryLabel) currentCategoryLabel.textContent = category.label;
          renderCandidates();
          closeDropdown();
        });
        categoryDropdown.appendChild(button);
      });
    }

    function renderCandidates() {
      if (!candidatesList) return;
      const list = candidatesData[selectedCategory] || [];
      candidatesList.innerHTML = '';
      list.forEach((candidate, index) => {
        const wrapper = document.createElement('div');
        const rowHtml = `
          <div class="flex items-center justify-between p-6 hover:bg-gray-50 transition-colors">
            <div class="flex items-center space-x-4">
              <div class="w-16 h-16 rounded-lg overflow-hidden bg-gray-200">
                <img src="${candidate.image}" alt="${candidate.name}" class="w-full h-full object-cover" />
              </div>
              <div>
                <button class="text-xl font-bold text-gray-900 hover:text-blue-600 transition-colors text-left js-candidate-name">${candidate.name}</button>
                <p class="text-gray-600 font-medium">${candidate.party}</p>
                <button class="text-blue-600 text-sm hover:underline js-more-details">More details...</button>
              </div>
            </div>
            <button class="bg-blue-600 text-white px-8 py-3 rounded-lg font-medium hover:bg-blue-700 transition-colors js-vote-now">Vote Now</button>
          </div>
        `;
        wrapper.innerHTML = index < list.length - 1 ? rowHtml + '<div class="border-b border-gray-200"></div>' : rowHtml;
        candidatesList.appendChild(wrapper);
        const nameBtn = wrapper.querySelector('.js-candidate-name');
        const detailsBtn = wrapper.querySelector('.js-more-details');
        const voteBtn = wrapper.querySelector('.js-vote-now');
        function showDetails() {
          selectedCandidate = candidate;
          if (detailImage) detailImage.src = candidate.image;
          if (detailImage) detailImage.alt = candidate.name;
          if (detailName) detailName.textContent = candidate.name;
          if (detailKey) detailKey.textContent = candidate.publicKey;
          if (aspirantsPage) aspirantsPage.classList.add('hidden');
          if (detailsPage) detailsPage.classList.remove('hidden');
          if (mobileNavDetails) mobileNavDetails.classList.add('hidden');
          if (menuIconDetails && closeIconDetails) {
            menuIconDetails.classList.remove('hidden');
            closeIconDetails.classList.add('hidden');
          }
          window.scrollTo({ top: 0, behavior: 'smooth' });
        }
        nameBtn.addEventListener('click', showDetails);
        detailsBtn.addEventListener('click', showDetails);
        voteBtn.addEventListener('click', () => {
          console.log(`Voting for: ${candidate.name}`);
          alert(`Voting for: ${candidate.name}`);
        });
      });
    }

    if (categoryButton) categoryButton.addEventListener('click', toggleDropdown);
    document.addEventListener('click', (e) => {
      if (categoryButton && categoryDropdown && !categoryButton.contains(e.target) && !categoryDropdown.contains(e.target)) {
        closeDropdown();
      }
    });
    if (backButton) {
      backButton.addEventListener('click', () => {
        if (detailsPage) detailsPage.classList.add('hidden');
        if (aspirantsPage) aspirantsPage.classList.remove('hidden');
        if (mobileNav) mobileNav.classList.add('hidden');
        if (menuIcon && closeIcon) {
          menuIcon.classList.remove('hidden');
          closeIcon.classList.add('hidden');
        }
        window.scrollTo({ top: 0, behavior: 'smooth' });
      });
    }
    if (confirmButton) {
      confirmButton.addEventListener('click', () => {
        if (selectedCandidate) alert(`Confirmed candidate: ${selectedCandidate.name}`);
      });
    }

    renderCategoryOptions();
    renderCandidates();
  })();

  // ===== Election page logic =====
  (function initElection() {
    const positionsList = document.getElementById('positionsList');
    if (!positionsList) return;
    const mobileMenuToggle = document.getElementById('mobileMenuToggle');
    const menuIcon = document.getElementById('menuIcon');
    const closeIcon = document.getElementById('closeIcon');
    const mobileNav = document.getElementById('mobileNav');
    if (mobileMenuToggle && mobileNav && menuIcon && closeIcon) {
      mobileMenuToggle.addEventListener('click', () => {
        const hidden = mobileNav.classList.contains('hidden');
        mobileNav.classList.toggle('hidden');
        if (hidden) {
          menuIcon.classList.add('hidden');
          closeIcon.classList.remove('hidden');
        } else {
          menuIcon.classList.remove('hidden');
          closeIcon.classList.add('hidden');
        }
      });
    }
    const electionPositions = [
      { id: 'hod', title: 'HOD' },
      { id: 'exam-officer', title: 'Exam Officer' },
      { id: 'secretary1', title: 'Secretary' },
      { id: 'secretary2', title: 'Secretary' }
    ];
    function renderPositions() {
      positionsList.innerHTML = '';
      electionPositions.forEach((position, index) => {
        const container = document.createElement('div');
        const rowHtml = `
          <div class="flex items-center justify-between p-6 hover:bg-gray-50 transition-colors">
            <div><h3 class="text-xl font-medium text-gray-900">${position.title}</h3></div>
            <button class="bg-blue-600 text-white px-8 py-3 rounded-lg font-medium hover:bg-blue-700 transition-colors js-vote">Vote Now</button>
          </div>
        `;
        container.innerHTML = index < electionPositions.length - 1 ? rowHtml + '<div class="border-b border-gray-200"></div>' : rowHtml;
        positionsList.appendChild(container);
        const voteBtn = container.querySelector('.js-vote');
        voteBtn.addEventListener('click', () => {
          console.log(`Voting for: ${position.title}`);
          alert(`Voting for: ${position.title}`);
        });
      });
    }
    renderPositions();
  })();

  // ===== Home page logic =====
  (function initHome() {
    const teamGrid = document.getElementById('teamGrid');
    const daysBox = document.getElementById('daysBox');
    if (!teamGrid && !daysBox) return;
    const mobileMenuToggle = document.getElementById('mobileMenuToggle');
    const menuIcon = document.getElementById('menuIcon');
    const closeIcon = document.getElementById('closeIcon');
    const mobileNav = document.getElementById('mobileNav');
    if (mobileMenuToggle && mobileNav && menuIcon && closeIcon) {
      mobileMenuToggle.addEventListener('click', () => {
        const hidden = mobileNav.classList.contains('hidden');
        mobileNav.classList.toggle('hidden');
        if (hidden) {
          menuIcon.classList.add('hidden');
          closeIcon.classList.remove('hidden');
        } else {
          menuIcon.classList.remove('hidden');
          closeIcon.classList.add('hidden');
        }
      });
    }
    if (daysBox) {
      let timeLeft = { days: 2, hours: 12, minutes: 45 };
      const hoursBox = document.getElementById('hoursBox');
      const minutesBox = document.getElementById('minutesBox');
      function renderTime() {
        daysBox.textContent = String(timeLeft.days).padStart(2, '0');
        hoursBox.textContent = String(timeLeft.hours).padStart(2, '0');
        minutesBox.textContent = String(timeLeft.minutes).padStart(2, '0');
      }
      renderTime();
      setInterval(() => {
        let { days, hours, minutes } = timeLeft;
        if (minutes > 0) minutes--; else if (hours > 0) { hours--; minutes = 59; } else if (days > 0) { days--; hours = 23; minutes = 59; }
        timeLeft = { days, hours, minutes };
        renderTime();
      }, 60000);
    }
    if (teamGrid) {
      const teamMembers = [
        { name: 'Dr. Risikat Adebiyi', role: 'Project Supervisor', image: '/images/dr-risikat.jpg', imagePosition: 'center' },
        { name: 'Mustapha Aminu', role: 'Backend Engineer', image: '/images/mustapha.jpeg', imagePosition: 'center 5%' },
        { name: 'Raji A. Ridwan', role: 'Frontend Developer', image: '/images/ridwan.jpeg', imagePosition: 'center 7%' }
      ];
      function renderTeam() {
        teamGrid.innerHTML = '';
        teamMembers.forEach((member) => {
          const card = document.createElement('div');
          card.className = 'text-center group';
          card.innerHTML = `
            <div class="relative mb-6 overflow-hidden rounded-lg">
              <img src="${member.image}" alt="${member.name}" class="w-full h-64 object-cover group-hover:scale-105 transition-transform duration-300" style="object-position: ${member.imagePosition};" />
              <div class="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black to-transparent p-4">
                <h3 class="text-white font-bold text-lg">${member.name}</h3>
              </div>
            </div>
            <p class="text-blue-600 font-medium">${member.role}</p>
          `;
          teamGrid.appendChild(card);
        });
      }
      renderTeam();
    }
    const voteNowBtn = document.getElementById('voteNowBtn');
    if (voteNowBtn) {
      voteNowBtn.addEventListener('click', () => {
        alert('Navigate to voting page');
        console.log('Navigate to voting page');
      });
    }
  })();

  // ===== Live Results page logic =====
  (function initLiveResult() {
    const resultsContainer = document.getElementById('resultsContainer');
    if (!resultsContainer) return;
    const mobileMenuToggle = document.getElementById('mobileMenuToggle');
    const menuIcon = document.getElementById('menuIcon');
    const closeIcon = document.getElementById('closeIcon');
    const mobileNav = document.getElementById('mobileNav');
    if (mobileMenuToggle && mobileNav && menuIcon && closeIcon) {
      mobileMenuToggle.addEventListener('click', () => {
        const hidden = mobileNav.classList.contains('hidden');
        mobileNav.classList.toggle('hidden');
        if (hidden) {
          menuIcon.classList.add('hidden');
          closeIcon.classList.remove('hidden');
        } else {
          menuIcon.classList.remove('hidden');
          closeIcon.classList.add('hidden');
        }
      });
    }
    let isLive = true;
    const liveIndicator = document.getElementById('liveIndicator');
    const liveText = document.getElementById('liveText');
    const liveToggleBtn = document.getElementById('liveToggleBtn');
    function updateLiveUI() {
      if (!liveIndicator || !liveText || !liveToggleBtn) return;
      if (isLive) {
        liveIndicator.classList.add('bg-red-500', 'animate-pulse');
        liveIndicator.classList.remove('bg-gray-500');
        liveText.textContent = 'LIVE RESULTS';
        liveToggleBtn.textContent = 'Stop Live';
      } else {
        liveIndicator.classList.remove('bg-red-500', 'animate-pulse');
        liveIndicator.classList.add('bg-gray-500');
        liveText.textContent = 'FINAL RESULTS';
        liveToggleBtn.textContent = 'Start Live';
      }
    }
    if (liveToggleBtn) {
      liveToggleBtn.addEventListener('click', () => {
        isLive = !isLive;
        updateLiveUI();
        if (isLive) startLive(); else stopLive();
      });
    }
    let results = {
      hod: { title: 'HOD ASPIRANTS', totalVotes: 1000, candidates: [
        { id: 1, name: 'Mustapha Abdulazez', votes: 550, image: '/images/candidate1.jpg', party: 'Progressive Party' },
        { id: 2, name: 'Sarah Johnson', votes: 300, image: '/images/candidate2.jpg', party: 'Unity Alliance' },
        { id: 3, name: 'Ahmed Ibrahim', votes: 100, image: '/images/candidate3.jpg', party: 'Reform Movement' },
        { id: 4, name: 'Grace Adebayo', votes: 50, image: '/images/candidate4.jpg', party: 'Independent' }
      ]},
      examOfficer: { title: 'EXAM OFFICER', totalVotes: 1000, candidates: [
        { id: 5, name: 'Mustapha Abdulazez', votes: 550, image: '/images/candidate1.jpg', party: 'Academic Excellence' },
        { id: 6, name: 'Dr. Fatima Ali', votes: 300, image: '/images/candidate5.jpg', party: 'Education First' },
        { id: 7, name: 'Prof. John Smith', votes: 100, image: '/images/candidate6.jpg', party: 'Innovation Party' },
        { id: 8, name: 'Aisha Mohammed', votes: 50, image: '/images/candidate7.jpg', party: 'Independent' }
      ]},
      secretary1: { title: 'SECRETARY (Position 1)', totalVotes: 1000, candidates: [
        { id: 9, name: 'Mustapha Abdulazez', votes: 550, image: '/images/candidate1.jpg', party: 'Administrative Excellence' },
        { id: 10, name: 'Kemi Oluwaseun', votes: 300, image: '/images/candidate8.jpg', party: 'Efficient Governance' },
        { id: 11, name: 'David Okafor', votes: 100, image: '/images/candidate9.jpg', party: 'Transparency First' },
        { id: 12, name: 'Blessing Eze', votes: 50, image: '/images/candidate10.jpg', party: 'Independent' }
      ]},
      secretary2: { title: 'SECRETARY (Position 2)', totalVotes: 1000, candidates: [
        { id: 13, name: 'Mustapha Abdulazez', votes: 550, image: '/images/candidate1.jpg', party: 'Digital Transformation' },
        { id: 14, name: 'Yusuf Hassan', votes: 300, image: '/images/candidate11.jpg', party: 'Modern Administration' },
        { id: 15, name: 'Folake Adamu', votes: 100, image: '/images/candidate12.jpg', party: 'Progressive Alliance' },
        { id: 16, name: 'Chidi Okwu', votes: 50, image: '/images/candidate13.jpg', party: 'Independent' }
      ]}
    };
    function renderResults() {
      resultsContainer.innerHTML = '';
      Object.values(results).forEach((section) => {
        const sectionWrapper = document.createElement('div');
        sectionWrapper.className = 'mb-12';
        sectionWrapper.innerHTML = `
          <div class=\"bg-black text-white p-4 rounded-t-lg flex justify-between items-center\">\n            <div class=\"flex items-center space-x-3\">\n              <svg class=\"w-6 h-6\" fill=\"currentColor\" viewBox=\"0 0 24 24\"><path d=\"M16 11c1.654 0 3-1.346 3-3S17.654 5 16 5s-3 1.346-3 3 1.346 3 3 3zM8 13c2.206 0 4-1.794 4-4S10.206 5 8 5 4 6.794 4 9s1.794 4 4 4zm8 2c-2.67 0-8 1.337-8 4v1h16v-1c0-2.663-5.33-4-8-4zM8 15c-2.67 0-8 1.337-8 4v1h8v-1c0-1.06.492-2.062 1.344-2.885C8.895 15.042 8.456 15 8 15z\"/></svg>\n              <h2 class=\"text-xl font-bold\">${section.title}</h2>\n            </div>\n            <div class=\"flex items-center space-x-2\">\n              <svg class=\"w-5 h-5\" fill=\"currentColor\" viewBox=\"0 0 24 24\"><path d=\"M3 3v18h18V3H3zm16 16H5V5h14v14zM7 15h2V7H7v8zm4 4h2V7h-2v12zm4-6h2V7h-2v8z\"/></svg>\n              <span class=\"font-medium\">${(section.totalVotes || 0).toLocaleString()} Votes</span>\n            </div>\n          </div>\n          <div class=\"grid md:grid-cols-2 gap-4 p-6 bg-gray-100 rounded-b-lg js-cards\"></div>
        `;
        const cards = sectionWrapper.querySelector('.js-cards');
        const sorted = [...section.candidates].sort((a, b) => b.votes - a.votes);
        const totalVotes = section.totalVotes || sorted.reduce((s, c) => s + c.votes, 0);
        sorted.forEach((candidate, idx) => {
          const percentage = totalVotes > 0 ? Math.round((candidate.votes / totalVotes) * 100) : 0;
          const gradient = idx === 0 ? 'from-green-400 to-green-600' : idx === 1 ? 'from-orange-400 to-orange-600' : idx === 2 ? 'from-orange-500 to-orange-700' : 'from-red-400 to-red-600';
          const card = document.createElement('div');
          card.className = 'bg-white rounded-lg shadow-lg overflow-hidden hover:shadow-xl transition-shadow';
          card.innerHTML = `
            <div class=\"flex\">\n              <div class=\"bg-gradient-to-br ${gradient} p-4 flex items-center space-x-4 flex-1\">\n                <img src=\"${candidate.image || '/images/default-avatar.jpg'}\" alt=\"${candidate.name}\" class=\"w-16 h-16 rounded-full object-cover border-3 border-white shadow-lg\" />\n                <div class=\"text-white\">\n                  <h3 class=\"font-bold text-lg\">${candidate.name}</h3>\n                  <p class=\"text-sm opacity-90\">${candidate.party || 'Independent'}<\/p>\n                <\/div>\n              <\/div>\n              <div class=\"bg-gray-50 p-4 flex flex-col justify-center items-center min-w-[120px]\">\n                <div class=\"text-3xl font-bold text-gray-900 mb-1\">${percentage}%<\/div>\n                <div class=\"text-sm text-blue-600 font-medium\">${candidate.votes.toLocaleString()} Votes<\/div>\n                ${idx === 0 ? '<div class=\\"flex items-center mt-2 text-green-600\\"><svg class=\\"w-4 h-4 mr-1\\" fill=\\"currentColor\\" viewBox=\\"0 0 24 24\\"><path d=\\"M12 2l3 7h7l-5.5 4.5L18 22l-6-4-6 4 1.5-8.5L2 9h7z\\"/><\/svg><span class=\\"text-xs font-medium\\">Leading<\/span><\/div>' : ''}\n              <\/div>\n            <\/div>
          `;
          cards.appendChild(card);
        });
        resultsContainer.appendChild(sectionWrapper);
      });
    }
    let liveInterval = null;
    function startLive() {
      if (liveInterval) return;
      liveInterval = setInterval(() => {
        Object.keys(results).forEach((key) => {
          const section = results[key];
          section.candidates = section.candidates.map((c) => ({ ...c, votes: c.votes + Math.floor(Math.random() * 3) }));
          section.totalVotes = section.candidates.reduce((s, c) => s + c.votes, 0);
        });
        renderResults();
      }, 5000);
    }
    function stopLive() {
      if (liveInterval) { clearInterval(liveInterval); liveInterval = null; }
    }
    updateLiveUI();
    renderResults();
    if (isLive) startLive();
  })();

  // ===== OTP Verification page logic =====
  (function initOtp() {
    const form = document.getElementById('otpForm');
    if (!form) return;
    const inputsContainer = document.getElementById('otpInputs');
    const inputs = Array.from(inputsContainer.querySelectorAll('input'));
    inputs.forEach((input, idx) => {
      input.addEventListener('input', (e) => {
        const value = e.target.value.replace(/\D/g, '');
        e.target.value = value.slice(0, 1);
        if (value && idx < inputs.length - 1) inputs[idx + 1].focus();
      });
      input.addEventListener('keydown', (e) => {
        if (e.key === 'Backspace' && !input.value && idx > 0) inputs[idx - 1].focus();
      });
    });
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      const otpCode = inputs.map((i) => i.value).join('');
      console.log('OTP submitted:', otpCode);
      alert('OTP submitted: ' + otpCode);
    });
  })();

  // ===== Voting page logic =====
  (function initVoting() {
    const positionsContainer = document.getElementById('positionsContainer');
    if (!positionsContainer) return;
    const votingPage = document.getElementById('votingPage');
    const votingCompleteView = document.getElementById('votingCompleteView');
    const mobileMenuToggle = document.getElementById('mobileMenuToggle');
    const menuIcon = document.getElementById('menuIcon');
    const closeIcon = document.getElementById('closeIcon');
    const mobileNav = document.getElementById('mobileNav');
    if (mobileMenuToggle && mobileNav && menuIcon && closeIcon) {
      mobileMenuToggle.addEventListener('click', () => {
        const hidden = mobileNav.classList.contains('hidden');
        mobileNav.classList.toggle('hidden');
        if (hidden) { menuIcon.classList.add('hidden'); closeIcon.classList.remove('hidden'); }
        else { menuIcon.classList.remove('hidden'); closeIcon.classList.add('hidden'); }
      });
    }
    const progressText = document.getElementById('progressText');
    const submitVotesBtn = document.getElementById('submitVotesBtn');
    const voteModal = document.getElementById('voteModal');
    const modalCandidate = document.getElementById('modalCandidate');
    const modalPosition = document.getElementById('modalPosition');
    const modalConfirmBtn = document.getElementById('modalConfirmBtn');
    const modalBackBtn = document.getElementById('modalBackBtn');
    const viewResultsBtn = document.getElementById('viewResultsBtn');
    const positions = [
      { id: 'hod', title: 'HOD', candidates: ['Dr. Johnson Smith', 'Prof. Sarah Williams', 'Dr. Michael Brown'] },
      { id: 'examOfficer', title: 'Exam Officer', candidates: ['Dr. Emily Davis', 'Prof. Robert Wilson', 'Dr. Lisa Anderson'] },
      { id: 'secretary1', title: 'Secretary (Position 1)', candidates: ['John Thompson', 'Mary Johnson', 'David Lee'] },
      { id: 'secretary2', title: 'Secretary (Position 2)', candidates: ['Anna Martinez', 'James Taylor', 'Jennifer White'] }
    ];
    const selectedPositions = {};
    let pendingVote = { position: '', candidate: '', positionTitle: '' };
    function renderPositions() {
      positionsContainer.innerHTML = '';
      positions.forEach((position) => {
        const section = document.createElement('div');
        section.className = 'bg-white rounded-lg shadow-sm border border-gray-200 p-6';
        section.innerHTML = `<h2 class="text-xl font-semibold text-gray-900 mb-6">${position.title}</h2><div class="grid gap-4 md:grid-cols-3 js-cards"></div>`;
        const cards = section.querySelector('.js-cards');
        position.candidates.forEach((candidate, index) => {
          const isSelected = selectedPositions[position.id] === candidate;
          const card = document.createElement('div');
          card.className = 'border border-gray-200 rounded-lg p-4 hover:border-blue-300 transition-colors';
          card.innerHTML = `
            <div class=\"flex items-center justify-between\">\n              <div>\n                <h3 class=\"font-medium text-gray-900\">${candidate}</h3>\n                <p class=\"text-sm text-gray-500\">Candidate ${index + 1}</p>\n              </div>\n              <button class=\"px-4 py-2 rounded-lg font-medium transition-colors ${isSelected ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-700 hover:bg-blue-50 hover:text-blue-600'}\">${isSelected ? 'Selected' : 'Vote'}</button>\n            </div>
          `;
          const voteBtn = card.querySelector('button');
          voteBtn.addEventListener('click', () => openVoteModal(position.id, candidate, position.title));
          cards.appendChild(card);
        });
        positionsContainer.appendChild(section);
      });
      updateProgress();
    }
    function updateProgress() {
      const voted = Object.keys(selectedPositions).length;
      progressText.textContent = `${voted} of ${positions.length} positions voted`;
    }
    function openVoteModal(positionId, candidate, positionTitle) {
      pendingVote = { position: positionId, candidate, positionTitle };
      modalCandidate.textContent = candidate;
      modalPosition.textContent = positionTitle;
      voteModal.classList.remove('hidden');
      voteModal.classList.add('flex');
    }
    function closeVoteModal() {
      voteModal.classList.add('hidden');
      voteModal.classList.remove('flex');
    }
    modalConfirmBtn.addEventListener('click', () => {
      selectedPositions[pendingVote.position] = pendingVote.candidate;
      pendingVote = { position: '', candidate: '', positionTitle: '' };
      closeVoteModal();
      renderPositions();
    });
    modalBackBtn.addEventListener('click', () => { pendingVote = { position: '', candidate: '', positionTitle: '' }; closeVoteModal(); });
    submitVotesBtn.addEventListener('click', () => {
      if (Object.keys(selectedPositions).length === positions.length) {
        votingPage.classList.add('hidden');
        votingCompleteView.classList.remove('hidden');
      } else { alert('Please vote for all positions before submitting.'); }
    });
    if (viewResultsBtn) viewResultsBtn.addEventListener('click', () => { console.log('Navigate to results page'); alert('Navigate to results page'); });
    renderPositions();
  })();
});



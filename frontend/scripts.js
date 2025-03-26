document.addEventListener('DOMContentLoaded', function() {
    // Tab functionality
    const tabs = document.querySelectorAll('.tab');
    tabs.forEach(tab => {
        tab.addEventListener('click', function() {
            // Remove active class from all tabs
            tabs.forEach(t => t.classList.remove('active'));
            // Add active class to clicked tab
            this.classList.add('active');
            
            // Hide all tab content
            const tabContents = document.querySelectorAll('.tab-content');
            tabContents.forEach(content => content.classList.remove('active'));
            
            // Show the selected tab content
            const tabId = this.getAttribute('data-tab');
            document.getElementById(tabId).classList.add('active');
        });
    });
    
    // File upload handling
    const dropArea = document.getElementById('dropArea');
    const fileInput = document.getElementById('resumeFile');
    const fileInfo = document.getElementById('fileInfo');
    const fileName = document.getElementById('fileName');
    const fileSize = document.getElementById('fileSize');
    const removeFileBtn = document.getElementById('removeFile');
    const progressContainer = document.getElementById('progressContainer');
    const progressBar = document.getElementById('progressBar');
    const errorMessage = document.getElementById('errorMessage');
    const errorText = document.getElementById('errorText');
    const statusChip = document.getElementById('statusChip');
    
    dropArea.addEventListener('click', () => {
        fileInput.click();
    });
    
    // Prevent default behavior for drag and drop
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, preventDefaults, false);
    });
    
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    // Highlight drop area when file is dragged over
    ['dragenter', 'dragover'].forEach(eventName => {
        dropArea.addEventListener(eventName, highlight, false);
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, unhighlight, false);
    });
    
    function highlight() {
        dropArea.classList.add('dragover');
    }
    
    function unhighlight() {
        dropArea.classList.remove('dragover');
    }
    
    // Handle dropped files
    dropArea.addEventListener('drop', handleDrop, false);
    
    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        handleFiles(files);
    }
    
    fileInput.addEventListener('change', function() {
        handleFiles(this.files);
    });
    
    function handleFiles(files) {
        if (files.length > 0) {
            const file = files[0];
            
            // Check file type
            const allowedTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/rtf'];
            if (!allowedTypes.includes(file.type)) {
                showError('Invalid file type. Please upload PDF, DOCX, or RTF file.');
                return;
            }
            
            // Check file size (limit to 5MB)
            if (file.size > 5 * 1024 * 1024) {
                showError('File size exceeds 5MB limit.');
                return;
            }
            
            // Display file info
            fileName.textContent = file.name;
            fileSize.textContent = `(${formatFileSize(file.size)})`;
            fileInfo.style.display = 'flex';
            errorMessage.style.display = 'none';
        }
    }
    
    function formatFileSize(bytes) {
        if (bytes < 1024) return bytes + ' bytes';
        else if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
        else return (bytes / 1048576).toFixed(1) + ' MB';
    }
    
    function showError(message) {
        errorText.textContent = message;
        errorMessage.style.display = 'flex';
    }
    
    removeFileBtn.addEventListener('click', function() {
        fileInput.value = '';
        fileInfo.style.display = 'none';
        statusChip.style.display = 'none';
    });
    
    // Form submission
// Replace the existing form submission handler with this:
uploadForm.addEventListener('submit', async function(e) {
    e.preventDefault();
    
    if (!fileInput.files.length) {
        showError('Please select a file to upload.');
        return;
    }
    
    // Show loading state
    submitBtn.disabled = true;
    progressContainer.style.display = 'block';
    document.getElementById('loading').style.display = 'flex';
    
    try {
        const formData = new FormData();
        formData.append('file', fileInput.files[0]);
        
        // Simulate upload progress (remove in production)
        let progress = 0;
        const progressInterval = setInterval(() => {
            progress += 10;
            progressBar.style.width = `${progress}%`;
            if (progress >= 100) clearInterval(progressInterval);
        }, 200);
        
        // Send to backend
        const response = await fetch('/api/upload/', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Upload failed');
        }
        
        const data = await response.json();
        updateUIWithResults(data);
        
    } catch (error) {
        showError(error.message);
        console.error('Upload error:', error);
    } finally {
        submitBtn.disabled = false;
        document.getElementById('loading').style.display = 'none';
    }
;

        const submitBtn = document.getElementById('submitBtn');
        const loading = document.getElementById('loading');

        // Disable submit button and show loading
        submitBtn.disabled = true;
        loading.style.display = 'flex';
        errorMessage.style.display = 'none';
        
        // Show progress bar
        progressContainer.style.display = 'block';
        progressBar.style.width = '0%';
        
        // Simulate upload progress
        let progress = 0;
        const interval = setInterval(() => {
            progress += 5;
            progressBar.style.width = progress + '%';
            
            if (progress >= 100) {
                clearInterval(interval);
            }
        }, 100);

        // Prepare form data
        const formData = new FormData();
        formData.append('file', fileInput.files[0]);

        try {
            const response = await fetch('/upload/', {
                method: 'POST',
                body: formData,
            });
        
            if (!response.ok) {
                throw new Error('Failed to upload resume. Please try again.');
            }
        
            const data = await response.json();
            
            // Update status
            statusChip.style.display = 'inline-flex';
            
            // Display parsed data in the appropriate sections
            populateResumeData(data.parsed_data);
            
            // Display matched jobs
            populateJobMatches(data.matched_jobs);
            
        } catch (error) {
            showError('An error occurred. ' + error.message);
            console.error('Error:', error);
            
            // For demo purposes, show sample data if API fails
            if (process.env.NODE_ENV === 'development') {
                simulateSuccessfulAnalysis();
            }
        } finally {
            submitBtn.disabled = false;
            loading.style.display = 'none';
            progressContainer.style.display = 'none';
        }
    });
    
    function populateResumeData(data) {
        // Populate personal information
        if (data.personal_info) {
            const personalInfo = [
                `Name: ${data.personal_info.name || 'N/A'}`,
                `Email: ${data.personal_info.email || 'N/A'}`,
                `Phone: ${data.personal_info.phone || 'N/A'}`,
                `Location: ${data.personal_info.location || 'N/A'}`
            ].join('\n');
            document.getElementById('personalInfo').textContent = personalInfo;
        }
        
        // Populate work experience
        if (data.work_experience && data.work_experience.length) {
            const workExp = data.work_experience.map(job => {
                return `${job.title}\n${job.company} | ${job.date_range}\n${job.responsibilities.map(r => `• ${r}`).join('\n')}`;
            }).join('\n\n');
            document.getElementById('workExperience').textContent = workExp;
        }
        
        // Populate education
        if (data.education && data.education.length) {
            const education = data.education.map(edu => {
                return `${edu.degree}\n${edu.institution} | ${edu.date_range}`;
            }).join('\n\n');
            document.getElementById('education').textContent = education;
        }
        
        // Populate skills
        if (data.skills) {
            const skillsText = Object.entries(data.skills).map(([category, skills]) => {
                return `${category}: ${skills.join(', ')}`;
            }).join('\n');
            document.getElementById('skills').textContent = skillsText;
            
            // Create skill tags
            const skillTags = document.getElementById('skillTags');
            skillTags.innerHTML = '';
            
            // Flatten skills array
            const allSkills = [];
            Object.values(data.skills).forEach(skillArray => {
                allSkills.push(...skillArray);
            });
            
            // Display up to 10 skills as tags
            allSkills.slice(0, 10).forEach(skill => {
                const tag = document.createElement('div');
                tag.className = 'skill-tag';
                tag.textContent = skill;
                skillTags.appendChild(tag);
            });
        }
    }
    
    function populateJobMatches(jobs) {
        const jobList = document.getElementById('jobList');
        
        if (!jobs || !jobs.length) {
            jobList.innerHTML = '<p>No job matches found. Try uploading a different resume.</p>';
            return;
        }
        
        jobList.innerHTML = '';
        
        jobs.forEach(job => {
            const matchingSkills = job.matching_skills || [];
            const missingSkills = job.missing_skills || [];
            
            const jobCard = document.createElement('div');
            jobCard.className = 'job-card';
            jobCard.innerHTML = `
                <div class="job-logo">
                    <i class="fas fa-building"></i>
                </div>
                <div class="job-info">
                    <h3>${job.title}</h3>
                    <div class="job-meta">
                        <div><i class="fas fa-building"></i> ${job.company}</div>
                        <div><i class="fas fa-map-marker-alt"></i> ${job.location}</div>
                        <div><i class="fas fa-clock"></i> ${job.employment_type || 'Full-time'}</div>
                    </div>
                    <div class="job-description">
                        ${job.description}
                    </div>
                    <div class="job-expand" data-job-id="${job.id}">
                        <i class="fas fa-chevron-down"></i> View details
                    </div>
                    <div class="matching-skills">
                        ${matchingSkills.map(skill => `
                            <div class="matching-skill"><i class="fas fa-check"></i> ${skill}</div>
                        `).join('')}
                        ${missingSkills.map(skill => `
                            <div class="matching-skill missing-skill"><i class="fas fa-times"></i> ${skill}</div>
                        `).join('')}
                    </div>
                </div>
                <div class="match-score">
                    <div class="match-percentage" style="background: conic-gradient(var(--success) 0% ${job.match_percentage}%, #f0f0f0 ${job.match_percentage}% 100%);">
                        <span>${job.match_percentage}%</span>
                    </div>
                    <span class="match-label">Match</span>
                </div>
            `;
            
            jobList.appendChild(jobCard);
            
            // Add event listener to expand button
            const expandBtn = jobCard.querySelector('.job-expand');
            expandBtn.addEventListener('click', () => {
                openJobModal(job);
            });
        });
    }
    
    // For development/demo purposes
    function simulateSuccessfulAnalysis() {
        // Update status
        statusChip.style.display = 'inline-flex';
        
        // Sample data
        const sampleData = {
            personal_info: {
                name: 'John Doe',
                email: 'john.doe@example.com',
                phone: '(555) 123-4567',
                location: 'San Francisco, CA'
            },
            work_experience: [
                {
                    title: 'Senior Developer',
                    company: 'Tech Innovations Inc.',
                    date_range: 'Jan 2020 - Present',
                    responsibilities: [
                        'Led development of cloud-based applications',
                        'Managed team of 5 developers',
                        'Implemented CI/CD pipeline reducing deployment time by 40%'
                    ]
                },
                {
                    title: 'Software Engineer',
                    company: 'Global Solutions',
                    date_range: 'Mar 2016 - Dec 2019',
                    responsibilities: [
                        'Implemented RESTful APIs',
                        'Developed front-end components using React',
                        'Optimized database queries improving performance by 25%'
                    ]
                }
            ],
            education: [
                {
                    degree: 'M.S. Computer Science',
                    institution: 'Stanford University',
                    date_range: '2014 - 2016'
                },
                {
                    degree: 'B.S. Computer Engineering',
                    institution: 'University of California, Berkeley',
                    date_range: '2010 - 2014'
                }
            ],
            skills: {
                'Programming Languages': ['JavaScript', 'Python', 'Java'],
                'Frameworks': ['React', 'Node.js', 'Express'],
                'Tools': ['Git', 'Docker', 'Jenkins'],
                'Databases': ['MongoDB', 'PostgreSQL']
            }
        };
        
        populateResumeData(sampleData);
        
        // Sample job matches
        const sampleJobs = [
            {
                id: 1,
                title: 'Senior Software Engineer',
                company: 'Tech Solutions Inc.',
                location: 'San Francisco, CA',
                employment_type: 'Full-time',
                description: 'Responsible for designing and implementing high-performance, scalable software solutions for enterprise clients. Collaborate with cross-functional teams to deliver innovative products.',
                match_percentage: 85,
                matching_skills: ['React', 'Node.js', 'JavaScript'],
                missing_skills: ['AWS', 'TypeScript']
            },
            {
                id: 2,
                title: 'Full Stack Developer',
                company: 'Innovation Labs',
                location: 'Remote',
                employment_type: 'Full-time',
                description: 'Join our team to build modern web applications using the latest technologies. You will work on both front-end and back-end development for our suite of products.',
                match_percentage: 92,
                matching_skills: ['JavaScript', 'React', 'MongoDB', 'Node.js'],
                missing_skills: ['GraphQL']
            },
            {
                id: 3,
                title: 'DevOps Engineer',
                company: 'Cloud Systems',
                location: 'Austin, TX',
                employment_type: 'Full-time',
                description: 'Help us build and maintain our cloud infrastructure. You will be responsible for implementing CI/CD pipelines and ensuring system reliability.',
                match_percentage: 74,
                matching_skills: ['Docker', 'Git'],
                missing_skills: ['Kubernetes', 'Terraform', 'AWS']
            }
        ];
        
        populateJobMatches(sampleJobs);
    }
    
    // Modal functionality
    const modal = document.getElementById('jobModal');
    const closeBtn = modal.querySelector('.modal-close');
    
    function openJobModal(job) {
        const modalTitle = modal.querySelector('.modal-title');
        const modalBody = modal.querySelector('.modal-body');
        
        // If job data is provided, use it to populate the modal
        if (job) {
            modalTitle.textContent = job.title;
            
            modalBody.innerHTML = `
                <h3>${job.title}</h                </h3>
                <p><strong>Company:</strong> ${job.company}</p>
                <p><strong>Location:</strong> ${job.location}</p>
                <p><strong>Employment Type:</strong> ${job.employment_type || 'Full-time'}</p>
                <p><strong>Description:</strong> ${job.description}</p>
                <h4>Matching Skills</h4>
                <ul>
                    ${job.matching_skills.map(skill => `<li><i class="fas fa-check"></i> ${skill}</li>`).join('')}
                </ul>
                <h4>Missing Skills</h4>
                <ul>
                    ${job.missing_skills.map(skill => `<li class="missing-skill"><i class="fas fa-times"></i> ${skill}</li>`).join('')}
                </ul>
                <div class="match-score">
                    <div class="match-percentage" style="background: conic-gradient(var(--success) 0% ${job.match_percentage}%, #f0f0f0 ${job.match_percentage}% 100%);">
                        <span>${job.match_percentage}%</span>
                    </div>
                    <span class="match-label">Match</span>
                </div>
                <button class="apply-button" onclick="window.open('${job.apply_link}', '_blank')">Apply Now</button>
            `;
        }

        modal.style.display = 'block';
    }

    closeBtn.addEventListener('click', () => {
        modal.style.display = 'none';
    });

    window.addEventListener('click', (event) => {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    });
});

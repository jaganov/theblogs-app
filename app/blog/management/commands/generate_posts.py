from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import random
import requests
import os
from faker import Faker
from account.models import CustomUser
from blog.models import Post

class Command(BaseCommand):
    help = 'Generate 40 posts for each user with themed content using Faker, Markdown, and Picsum Photos images'

    def __init__(self):
        super().__init__()
        # Initialize Faker with multiple locales for variety
        self.fakers = {
            'en_US': Faker('en_US'),
            'en_GB': Faker('en_GB'),
            'en_CA': Faker('en_CA'),
        }

    def get_picsum_image(self, topic, width=800, height=600):
        """Get random image from Picsum Photos based on topic"""
        try:
            # Picsum Photos provides random images with specific IDs
            # We'll use topic to generate a consistent ID for similar topics
            import hashlib
            
            # Create a hash from topic to get consistent image for similar topics
            topic_hash = hashlib.md5(topic.lower().encode()).hexdigest()
            # Convert first 8 characters of hash to integer for image ID
            image_id = int(topic_hash[:8], 16) % 1000 + 1  # IDs from 1 to 1000
            
            url = f"https://picsum.photos/id/{image_id}/{width}/{height}"
            
            self.stdout.write(f'    Requesting image from: {url}')
            
            # Test if the image exists
            response = requests.head(url, timeout=10)
            
            if response.status_code == 200:
                self.stdout.write(f'    Image URL resolved: {url}')
                return url
            else:
                # If specific ID doesn't exist, use random image
                random_url = f"https://picsum.photos/{width}/{height}"
                self.stdout.write(f'    Using random image: {random_url}')
                return random_url
                
        except requests.exceptions.Timeout:
            self.stdout.write(
                self.style.WARNING(f'Timeout getting Picsum image for {topic}')
            )
            return None
        except requests.exceptions.RequestException as e:
            self.stdout.write(
                self.style.WARNING(f'Request failed for Picsum image {topic}: {e}')
            )
            return None
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f'Unexpected error getting Picsum image for {topic}: {e}')
            )
            return None

    def download_and_save_image(self, image_url, topic, post_id):
        """Download image and save to media directory"""
        try:
            if not image_url:
                self.stdout.write(
                    self.style.WARNING(f'No image URL provided for {topic}')
                )
                return None, None
            
            # Create media directory if it doesn't exist
            # Use absolute path from Django settings
            from django.conf import settings
            media_dir = os.path.join(settings.MEDIA_ROOT, 'blog_images')
            
            # Ensure the directory exists
            try:
                os.makedirs(media_dir, exist_ok=True)
                self.stdout.write(f'    Directory created/verified: {media_dir}')
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Failed to create directory {media_dir}: {e}')
                )
                return None, None
            
            # Download image with better error handling
            try:
                response = requests.get(image_url, timeout=15, stream=True)
                response.raise_for_status()  # Raise exception for bad status codes
                
                # Check content type to ensure it's an image
                content_type = response.headers.get('content-type', '')
                if not content_type.startswith('image/'):
                    self.stdout.write(
                        self.style.WARNING(f'URL does not point to an image: {content_type}')
                    )
                    return None, None
                
            except requests.exceptions.RequestException as e:
                self.stdout.write(
                    self.style.ERROR(f'Failed to download image from {image_url}: {e}')
                )
                return None, None
            
            # Generate filename with better sanitization
            safe_topic = "".join(c for c in topic.lower() if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_topic = safe_topic.replace(' ', '_')
            filename = f"post_{post_id}_{safe_topic}.jpg"
            filepath = os.path.join(media_dir, filename)
            
            # Save image
            try:
                with open(filepath, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                
                # Verify file was created and has content
                if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
                    self.stdout.write(f'    Image saved: {filename} ({os.path.getsize(filepath)} bytes)')
                else:
                    self.stdout.write(
                        self.style.ERROR(f'File was not created or is empty: {filepath}')
                    )
                    return None, None
                
            except IOError as e:
                self.stdout.write(
                    self.style.ERROR(f'Failed to save image to {filepath}: {e}')
                )
                return None, None
            
            # Generate caption
            caption = self.generate_image_caption(topic)
            
            # Return relative path for Django model
            return f"blog_images/{filename}", caption
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Unexpected error downloading image for {topic}: {e}')
            )
            return None, None

    def generate_image_caption(self, topic):
        """Generate a descriptive caption for the image"""
        fake = random.choice(list(self.fakers.values()))
        
        caption_templates = [
            f"Visual representation of {topic.lower()} concepts and principles",
            f"Professional illustration showcasing {topic.lower()} techniques",
            f"Modern approach to {topic.lower()} in contemporary settings",
            f"Expert demonstration of {topic.lower()} methodologies",
            f"Comprehensive overview of {topic.lower()} best practices",
            f"Practical application of {topic.lower()} in real-world scenarios",
            f"Innovative solutions for {topic.lower()} challenges",
            f"Advanced techniques in {topic.lower()} implementation"
        ]
        
        return random.choice(caption_templates)

    def generate_markdown_content(self, topic, content_type='article'):
        """Generate realistic content with Markdown formatting"""
        
        # Choose random Faker for variety
        fake = random.choice(list(self.fakers.values()))
        
        if content_type == 'article':
            # Generate structured article with Markdown
            sections = []
            
            # Introduction
            intro_templates = [
                f"# {topic}: A Comprehensive Guide\n\nIn today's rapidly evolving world, {topic.lower()} has become an essential skill for professionals across various industries. This comprehensive guide will explore the fundamental principles and advanced techniques that make {topic.lower()} such a powerful tool.",
                f"# Mastering {topic}\n\n{topic} represents one of the most important developments in modern technology. Whether you're a beginner or an experienced professional, understanding {topic.lower()} can significantly enhance your capabilities and career prospects.",
                f"# The Complete {topic} Handbook\n\nFrom basic concepts to advanced applications, this handbook covers everything you need to know about {topic.lower()}. We'll explore practical examples, best practices, and real-world applications.",
                f"# {topic}: From Theory to Practice\n\n{topic} combines theoretical knowledge with practical implementation. This guide will help you bridge the gap between understanding concepts and applying them effectively.",
                f"# Advanced {topic} Techniques\n\nDiscover the cutting-edge techniques and methodologies that make {topic.lower()} such a valuable skill in today's competitive landscape."
            ]
            sections.append(random.choice(intro_templates))
            
            # Main content sections
            for i in range(random.randint(3, 5)):
                section_title = fake.sentence(nb_words=4).rstrip('.')
                section_content = fake.paragraph(nb_sentences=random.randint(3, 6))
                section = f"\n## {section_title}\n\n{section_content}"
                sections.append(section)
            
            # Conclusion
            conclusion_templates = [
                f"\n## Conclusion\n\n{topic} continues to evolve and adapt to new challenges and opportunities. By mastering the principles outlined in this guide, you'll be well-equipped to navigate the complexities of {topic.lower()} and leverage its full potential for your projects and career growth.",
                f"\n## Final Thoughts\n\nThe journey to mastering {topic.lower()} is ongoing, but with dedication and the right approach, you can achieve significant results. Remember that {topic.lower()} is not just about technical skills—it's about understanding the broader context and applying knowledge effectively.",
                f"\n## Moving Forward\n\nAs you continue your exploration of {topic.lower()}, keep in mind that the field is constantly evolving. Stay curious, practice regularly, and don't hesitate to experiment with new approaches and techniques.",
                f"\n## Summary\n\n{topic} offers tremendous opportunities for those willing to invest time and effort in learning. The principles and techniques covered in this guide provide a solid foundation for further exploration and mastery.",
                f"\n## Next Steps\n\nNow that you have a comprehensive understanding of {topic.lower()}, consider how you can apply these concepts to your own projects. The real learning begins when you start implementing these ideas in practical scenarios."
            ]
            sections.append(random.choice(conclusion_templates))
            
            return '\n'.join(sections)
        
        elif content_type == 'tutorial':
            # Generate step-by-step tutorial with Markdown
            sections = []
            sections.append(f"# {topic}: Step-by-Step Tutorial\n\nThis comprehensive tutorial will guide you through the process of mastering {topic.lower()}. Follow each step carefully to build a solid foundation.")
            
            # Tutorial steps
            for i in range(random.randint(4, 7)):
                step_title = fake.sentence(nb_words=5).rstrip('.')
                step_content = fake.paragraph(nb_sentences=random.randint(2, 4))
                step_code = f"```\n# Example code for step {i+1}\n{fake.word()} = '{fake.word()}'\nprint(f'Step {i+1}: {{fake.word()}}')\n```"
                
                step = f"\n## Step {i+1}: {step_title}\n\n{step_content}\n\n{step_code}"
                sections.append(step)
            
            sections.append(f"\n## Congratulations!\n\nYou've successfully completed the {topic.lower()} tutorial. You now have the knowledge and skills to apply these concepts in your own projects.")
            
            return '\n'.join(sections)
        
        elif content_type == 'tips':
            # Generate tips and best practices with Markdown
            sections = []
            sections.append(f"# {topic}: Essential Tips and Best Practices\n\nDiscover the most effective strategies and techniques for mastering {topic.lower()}. These tips have been gathered from industry experts and experienced practitioners.")
            
            # Tips
            for i in range(random.randint(6, 10)):
                tip_title = fake.sentence(nb_words=4).rstrip('.')
                tip_content = fake.paragraph(nb_sentences=random.randint(2, 3))
                tip = f"\n## Tip {i+1}: {tip_title}\n\n{tip_content}"
                sections.append(tip)
            
            sections.append(f"\n## Implementation Strategy\n\nTo make the most of these {topic.lower()} tips, start by implementing them gradually. Focus on one or two tips at a time, practice consistently, and measure your progress.")
            
            return '\n'.join(sections)
        
        elif content_type == 'case_study':
            # Generate case study with Markdown
            sections = []
            sections.append(f"# {topic}: Real-World Case Study\n\nThis case study examines how {topic.lower()} was successfully implemented in a real-world scenario, providing valuable insights and lessons learned.")
            
            # Case study sections
            sections.append(f"\n## Background\n\n{fake.paragraph(nb_sentences=4)}")
            sections.append(f"\n## Challenge\n\n{fake.paragraph(nb_sentences=3)}")
            sections.append(f"\n## Solution\n\n{fake.paragraph(nb_sentences=4)}")
            sections.append(f"\n## Implementation\n\n{fake.paragraph(nb_sentences=3)}")
            sections.append(f"\n## Results\n\n{fake.paragraph(nb_sentences=3)}")
            sections.append(f"\n## Key Takeaways\n\n- {fake.sentence(nb_words=8).rstrip('.')}\n- {fake.sentence(nb_words=8).rstrip('.')}\n- {fake.sentence(nb_words=8).rstrip('.')}")
            
            return '\n'.join(sections)
        
        else:
            # Simple article with basic Markdown
            return f"# {topic}\n\n{fake.paragraph(nb_sentences=4)}\n\n## Key Points\n\n{fake.paragraph(nb_sentences=3)}\n\n## Conclusion\n\n{fake.paragraph(nb_sentences=2)}"

    def generate_excerpt(self, topic):
        """Generate a compelling excerpt for the post without Markdown"""
        fake = random.choice(list(self.fakers.values()))
        
        # Generate a comprehensive paragraph about the topic
        excerpt_templates = [
            f"In today's rapidly evolving landscape, {topic.lower()} has emerged as a critical skill that professionals across various industries need to master. This comprehensive exploration delves into the fundamental principles, advanced techniques, and practical applications that make {topic.lower()} such a valuable asset. Whether you're a beginner looking to establish a solid foundation or an experienced practitioner seeking to enhance your expertise, this guide provides the insights and strategies you need to succeed. From understanding core concepts to implementing real-world solutions, we'll cover everything you need to know about {topic.lower()} and how it can transform your approach to modern challenges.",
            
            f"The world of {topic.lower()} is constantly evolving, presenting both opportunities and challenges for those willing to explore its depths. This detailed examination reveals the essential strategies, best practices, and innovative approaches that define successful implementation of {topic.lower()} principles. Through practical examples and expert insights, you'll discover how to leverage {topic.lower()} effectively in your projects and career development. The comprehensive coverage includes fundamental concepts, advanced methodologies, and real-world applications that demonstrate the transformative power of {topic.lower()} in today's competitive environment.",
            
            f"Mastering {topic.lower()} requires a deep understanding of its underlying principles and practical applications in real-world scenarios. This extensive guide provides a thorough exploration of the techniques, strategies, and methodologies that professionals use to achieve excellence in {topic.lower()}. From foundational knowledge to advanced implementation strategies, you'll gain the expertise needed to navigate the complexities of {topic.lower()} with confidence. The insights shared here are drawn from industry experts and successful practitioners who have demonstrated the value of {topic.lower()} in achieving remarkable results.",
            
            f"Understanding {topic.lower()} is essential for anyone looking to stay competitive in today's dynamic professional landscape. This comprehensive resource offers an in-depth analysis of the key concepts, practical techniques, and strategic approaches that make {topic.lower()} such a powerful tool for success. Through detailed explanations and actionable insights, you'll learn how to apply {topic.lower()} principles effectively in various contexts. The guide covers everything from basic fundamentals to advanced applications, providing you with the knowledge and skills needed to excel in your field.",
            
            f"The significance of {topic.lower()} cannot be overstated in our modern, technology-driven world. This detailed exploration provides a complete overview of the essential elements, proven methodologies, and cutting-edge approaches that define excellence in {topic.lower()}. Whether you're starting your journey or looking to enhance existing skills, this guide offers valuable perspectives and practical strategies for achieving mastery. From theoretical foundations to hands-on implementation, you'll discover how {topic.lower()} can enhance your capabilities and open new opportunities for growth and advancement."
        ]
        
        # Select a random template and enhance it with additional Faker content
        base_excerpt = random.choice(excerpt_templates)
        
        # Add some variety by occasionally including additional context
        if random.choice([True, False]):
            additional_context = f" {fake.sentence(nb_words=12)} {fake.sentence(nb_words=10)}"
            base_excerpt += additional_context
        
        return base_excerpt

    def add_arguments(self, parser):
        parser.add_argument(
            '--image-chance',
            type=float,
            default=1.0,
            help='Probability of generating featured image for each post (0.0 to 1.0, default: 1.0)'
        )

    def handle(self, *args, **options):
        image_chance = options['image_chance']
        
        # Validate image_chance parameter
        if not 0.0 <= image_chance <= 1.0:
            self.stdout.write(
                self.style.ERROR('Image chance must be between 0.0 and 1.0')
            )
            return

        # Get all users
        users = CustomUser.objects.all()
        
        if not users.exists():
            self.stdout.write(
                self.style.ERROR('No users found. Please create users first using generate_users command.')
            )
            return

        # Define themed content for each user type
        user_themes = {
            'alex_writer': {
                'topics': [
                    'Python Best Practices', 'Django Development Tips', 'Web Development Trends',
                    'API Design Principles', 'Database Optimization', 'Code Review Guidelines',
                    'Testing Strategies', 'Deployment Best Practices', 'Security in Web Apps',
                    'Performance Optimization', 'Microservices Architecture', 'Cloud Computing',
                    'DevOps Practices', 'Frontend Frameworks', 'Backend Development',
                    'Mobile App Development', 'Machine Learning Basics', 'Data Science Tools',
                    'Version Control with Git', 'Agile Development', 'Code Documentation',
                    'Software Architecture', 'Design Patterns', 'Clean Code Principles',
                    'Debugging Techniques', 'Code Refactoring', 'Software Testing',
                    'Continuous Integration', 'Docker Containers', 'Kubernetes Basics',
                    'Serverless Computing', 'GraphQL vs REST', 'Web Security',
                    'Progressive Web Apps', 'Mobile-First Design', 'Responsive Web Design',
                    'CSS Frameworks', 'JavaScript ES6+', 'TypeScript Benefits',
                    'React Development', 'Vue.js Framework'
                ],
                'content_types': ['article', 'tutorial', 'tips'],
                'style': 'technical'
            },
            'maria_blogger': {
                'topics': [
                    'Morning Routine Optimization', 'Productivity Hacks', 'Goal Setting Strategies',
                    'Time Management Tips', 'Work-Life Balance', 'Mindfulness Practices',
                    'Personal Development', 'Habit Building', 'Stress Management',
                    'Digital Detox', 'Self-Care Routines', 'Career Growth',
                    'Networking Skills', 'Communication Tips', 'Leadership Development',
                    'Creative Thinking', 'Problem Solving', 'Decision Making',
                    'Emotional Intelligence', 'Confidence Building', 'Public Speaking',
                    'Writing Skills', 'Learning Strategies', 'Memory Techniques',
                    'Focus and Concentration', 'Energy Management', 'Sleep Optimization',
                    'Nutrition for Productivity', 'Exercise Routines', 'Mental Health',
                    'Relationship Building', 'Conflict Resolution', 'Team Collaboration',
                    'Remote Work Tips', 'Home Organization', 'Financial Planning',
                    'Travel Planning', 'Reading Habits', 'Journaling Benefits',
                    'Gratitude Practices', 'Positive Thinking'
                ],
                'content_types': ['article', 'tips', 'case_study'],
                'style': 'lifestyle'
            },
            'john_developer': {
                'topics': [
                    'Advanced Python Techniques', 'Django ORM Optimization', 'React Performance',
                    'Database Design Patterns', 'API Security', 'Microservices Design',
                    'Cloud Architecture', 'DevOps Automation', 'Code Quality Metrics',
                    'Testing Frameworks', 'Deployment Strategies', 'Monitoring Tools',
                    'Load Balancing', 'Caching Strategies', 'Database Sharding',
                    'Message Queues', 'Event-Driven Architecture', 'GraphQL Implementation',
                    'WebSocket Applications', 'Real-time Features', 'Mobile API Design',
                    'Authentication Systems', 'Authorization Patterns', 'Data Encryption',
                    'Backup Strategies', 'Disaster Recovery', 'Scalability Planning',
                    'Performance Profiling', 'Memory Optimization', 'CPU Optimization',
                    'Network Optimization', 'Security Auditing', 'Penetration Testing',
                    'Code Review Automation', 'Continuous Deployment', 'Infrastructure as Code',
                    'Container Orchestration', 'Service Mesh', 'Observability',
                    'Distributed Systems', 'Event Sourcing'
                ],
                'content_types': ['tutorial', 'article', 'case_study'],
                'style': 'advanced_technical'
            },
            'sarah_designer': {
                'topics': [
                    'UI Design Principles', 'UX Research Methods', 'Design Systems',
                    'Color Theory', 'Typography Design', 'Layout Composition',
                    'Visual Hierarchy', 'User Interface Patterns', 'Accessibility Design',
                    'Mobile Design', 'Responsive Design', 'Prototyping Tools',
                    'Design Thinking', 'User Journey Mapping', 'Information Architecture',
                    'Wireframing Techniques', 'Visual Design', 'Interaction Design',
                    'Animation in UI', 'Design Handoff', 'Design Collaboration',
                    'Design Critique', 'Design Portfolio', 'Design Trends',
                    'Brand Identity', 'Logo Design', 'Icon Design',
                    'Illustration Styles', 'Photography in Design', 'Grid Systems',
                    'White Space Usage', 'Contrast and Readability', 'Design Psychology',
                    'Emotional Design', 'Gamification Design', 'Dark Mode Design',
                    'Design for Different Cultures', 'Inclusive Design', 'Sustainable Design',
                    'Design Ethics', 'Future of Design'
                ],
                'content_types': ['article', 'tips', 'case_study'],
                'style': 'design'
            },
            'mike_entrepreneur': {
                'topics': [
                    'Business Model Canvas', 'Market Research', 'Customer Validation',
                    'Pitch Deck Creation', 'Funding Strategies', 'Investor Relations',
                    'Team Building', 'Leadership Skills', 'Strategic Planning',
                    'Financial Management', 'Revenue Models', 'Growth Strategies',
                    'Marketing Strategies', 'Sales Techniques', 'Customer Acquisition',
                    'Retention Strategies', 'Product Development', 'MVP Creation',
                    'Competitive Analysis', 'Risk Management', 'Legal Considerations',
                    'Intellectual Property', 'Partnership Building', 'Networking',
                    'Mentorship', 'Scaling Operations', 'Exit Strategies',
                    'Bootstrapping', 'Crowdfunding', 'Angel Investment',
                    'Venture Capital', 'Business Development', 'International Expansion',
                    'Digital Transformation', 'Innovation Management', 'Change Management',
                    'Corporate Culture', 'Remote Teams', 'Workplace Diversity',
                    'Sustainability in Business', 'Social Entrepreneurship'
                ],
                'content_types': ['article', 'tips', 'case_study'],
                'style': 'business'
            },
            'lisa_teacher': {
                'topics': [
                    'Active Learning Strategies', 'Differentiated Instruction', 'Assessment Methods',
                    'Classroom Management', 'Student Engagement', 'Technology in Education',
                    'Project-Based Learning', 'Flipped Classroom', 'Blended Learning',
                    'Special Education', 'Gifted Education', 'ESL Teaching',
                    'Curriculum Design', 'Lesson Planning', 'Educational Technology',
                    'Online Teaching', 'Student Motivation', 'Parent Communication',
                    'Professional Development', 'Educational Leadership', 'School Culture',
                    'Inclusive Education', 'Cultural Competency', 'Social-Emotional Learning',
                    'Critical Thinking', 'Creative Problem Solving', 'Collaborative Learning',
                    'Digital Literacy', 'Media Literacy', 'Information Literacy',
                    'Study Skills', 'Test Preparation', 'Academic Writing',
                    'Research Skills', 'Presentation Skills', 'Public Speaking',
                    'Debate and Discussion', 'Peer Teaching', 'Mentoring Students',
                    'Career Guidance', 'College Preparation'
                ],
                'content_types': ['tutorial', 'article', 'tips'],
                'style': 'educational'
            },
            'david_photographer': {
                'topics': [
                    'Composition Techniques', 'Lighting Fundamentals', 'Camera Settings',
                    'Portrait Photography', 'Landscape Photography', 'Street Photography',
                    'Event Photography', 'Product Photography', 'Macro Photography',
                    'Night Photography', 'HDR Photography', 'Black and White',
                    'Color Theory in Photography', 'Post-Processing', 'Photo Editing',
                    'RAW vs JPEG', 'Lens Selection', 'Tripod Usage',
                    'Filters and Accessories', 'Travel Photography', 'Wedding Photography',
                    'Documentary Photography', 'Fine Art Photography', 'Commercial Photography',
                    'Aerial Photography', 'Underwater Photography', 'Sports Photography',
                    'Wildlife Photography', 'Architectural Photography', 'Food Photography',
                    'Fashion Photography', 'Photojournalism', 'Stock Photography',
                    'Printing Techniques', 'Photo Books', 'Exhibition Planning',
                    'Photography Business', 'Marketing Photography', 'Client Relations',
                    'Copyright and Licensing', 'Photography Ethics'
                ],
                'content_types': ['tutorial', 'tips', 'case_study'],
                'style': 'creative'
            },
            'anna_chef': {
                'topics': [
                    'Knife Skills', 'Cooking Techniques', 'Flavor Pairing',
                    'Meal Planning', 'Budget Cooking', 'Quick Recipes',
                    'Slow Cooking', 'Baking Basics', 'Bread Making',
                    'Pasta Making', 'Sauce Making', 'Soup Making',
                    'Salad Making', 'Grilling Techniques', 'Roasting Methods',
                    'Steaming Techniques', 'Frying Methods', 'Smoking Food',
                    'Fermentation', 'Pickling', 'Canning',
                    'Food Preservation', 'Seasonal Cooking', 'Local Ingredients',
                    'Organic Cooking', 'Vegetarian Cooking', 'Vegan Cooking',
                    'Gluten-Free Cooking', 'Dairy-Free Cooking', 'Low-Carb Cooking',
                    'Mediterranean Cuisine', 'Asian Cuisine', 'Mexican Cuisine',
                    'Italian Cuisine', 'French Cuisine', 'Indian Cuisine',
                    'Middle Eastern Cuisine', 'African Cuisine', 'Dessert Making',
                    'Cocktail Making', 'Wine Pairing'
                ],
                'content_types': ['tutorial', 'tips', 'case_study'],
                'style': 'culinary'
            },
            'tom_fitness': {
                'topics': [
                    'Strength Training', 'Cardio Workouts', 'Flexibility Training',
                    'Core Exercises', 'Weight Loss', 'Muscle Building',
                    'Nutrition Basics', 'Meal Timing', 'Supplementation',
                    'Recovery Methods', 'Injury Prevention', 'Form and Technique',
                    'Workout Programming', 'Progressive Overload', 'Periodization',
                    'Functional Training', 'HIIT Workouts', 'Yoga for Fitness',
                    'Pilates', 'CrossFit', 'Bodyweight Exercises',
                    'Resistance Training', 'Endurance Training', 'Speed Training',
                    'Agility Training', 'Balance Training', 'Stability Training',
                    'Sports-Specific Training', 'Senior Fitness', 'Prenatal Fitness',
                    'Postpartum Fitness', 'Kids Fitness', 'Group Training',
                    'Personal Training', 'Online Coaching', 'Fitness Technology',
                    'Wearable Devices', 'Fitness Apps', 'Gym Equipment',
                    'Home Workouts', 'Outdoor Training'
                ],
                'content_types': ['tutorial', 'tips', 'case_study'],
                'style': 'fitness'
            },
            'emma_artist': {
                'topics': [
                    'Digital Painting', 'Character Design', 'Landscape Art',
                    'Portrait Drawing', 'Color Theory', 'Composition',
                    'Lighting and Shading', 'Perspective Drawing', 'Anatomy Drawing',
                    'Gesture Drawing', 'Sketching Techniques', 'Line Art',
                    'Watercolor Techniques', 'Oil Painting', 'Acrylic Painting',
                    'Mixed Media', 'Collage Art', 'Abstract Art',
                    'Concept Art', 'Illustration Styles', 'Comic Art',
                    'Animation Basics', '3D Modeling', 'Sculpture',
                    'Printmaking', 'Textile Art', 'Ceramics',
                    'Jewelry Making', 'Paper Crafts', 'Digital Sculpting',
                    'Texture Painting', 'Environment Design', 'Prop Design',
                    'Storyboarding', 'Visual Development', 'Art Direction',
                    'Art Business', 'Commission Work', 'Art Marketing',
                    'Art Portfolio', 'Art Exhibitions'
                ],
                'content_types': ['tutorial', 'tips', 'case_study'],
                'style': 'artistic'
            }
        }

        total_posts_created = 0
        
        for user in users:
            username = user.username
            if username not in user_themes:
                self.stdout.write(
                    self.style.WARNING(f'No theme defined for user {username}, skipping...')
                )
                continue

            theme = user_themes[username]
            topics = theme['topics']
            content_types = theme['content_types']
            style = theme['style']
            
            self.stdout.write(f'\nGenerating posts for {username} ({style} style)...')
            
            posts_created = 0
            for i in range(20):
                # Select random topic and content type
                topic = random.choice(topics)
                content_type = random.choice(content_types)
                
                # Generate content using our improved method with Markdown
                content = self.generate_markdown_content(topic, content_type)
                excerpt = self.generate_excerpt(topic)
                
                # Create varied titles
                title_templates = [
                    f"{topic}: A Complete Guide",
                    f"How to Master {topic}",
                    f"{topic}: Best Practices and Tips",
                    f"Everything You Need to Know About {topic}",
                    f"{topic}: What You Need to Know in 2024",
                    f"A Practical Guide to {topic}",
                    f"{topic}: Secrets to Success",
                    f"Learning {topic}: From Theory to Practice"
                ]
                title = random.choice(title_templates)
                
                # Create post with random date within last 6 months
                random_days_ago = random.randint(0, 180)
                random_date = timezone.now() - timedelta(days=random_days_ago)
                
                # Create post first to get the ID
                post = Post.objects.create(
                    title=title,
                    content=content,
                    excerpt=excerpt,
                    author=user,
                    status='published',
                    created_at=random_date
                )
                
                # Generate and download featured image based on image_chance parameter
                if random.random() < image_chance:
                    self.stdout.write(f'  Generating image for post: {title[:50]}...')
                    image_path, image_caption = self.download_and_save_image(
                        self.get_picsum_image(topic), 
                        topic, 
                        post.id
                    )
                    
                    if image_path and image_caption:
                        post.featured_image = image_path
                        post.image_caption = image_caption
                        post.save()
                        self.stdout.write(f'    ✓ Image added: {image_caption}')
                    else:
                        self.stdout.write(f'    ⚠ No image generated')
                else:
                    self.stdout.write(f'  Skipping image generation for post: {title[:50]} (chance: {image_chance})')
                
                posts_created += 1
                
                if posts_created % 10 == 0:
                    self.stdout.write(f'  Created {posts_created} posts...')
            
            total_posts_created += posts_created
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created {posts_created} posts for {username}')
            )

        self.stdout.write(
            self.style.SUCCESS(f'\nTotal posts created: {total_posts_created}')
        )
        self.stdout.write(
            self.style.SUCCESS('All posts have status: published')
        )
        self.stdout.write(
            self.style.SUCCESS(f'Image generation chance: {image_chance * 100:.0f}%')
        ) 
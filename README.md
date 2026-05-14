# Kinder Video Library

A secure, child-friendly web application built with [Django](https://www.djangoproject.com/?utm_source=chatgpt.com) that allows parents to create their own curated video libraries using videos from [YouTube](https://www.youtube.com/?utm_source=chatgpt.com).

The platform is designed to provide children with a safe viewing experience without advertisements, distracting recommendations, or unrestricted access to YouTube. Parents can organize approved videos into categories and manage everything through the built-in Django admin interface.

## Features

- User registration and authentication
- Multi-user architecture (each parent manages a private video library)
- Category-based organization of videos
- Embedded YouTube player using `youtube-nocookie.com`
- Child-friendly interface
- Django admin panel for content management
- Video activation/deactivation
- Custom sorting of categories and videos
- Optional child profiles with PIN protection and viewing limits
- Responsive design for desktop, tablet, and mobile devices

## Project Goals

The purpose of this project is to create a private alternative to YouTube Kids where parents have complete control over the content their children can watch.

Each user can:

- Create categories such as Cartoons, Educational Videos, Fairy Tales, Songs, or Language Learning
- Add YouTube links manually
- Display videos directly on the website
- Prevent children from navigating to YouTube or unrelated content
- Share the platform with family members or friends

## Technology Stack

- :contentReference[oaicite:2]{index=2}
- :contentReference[oaicite:3]{index=3}
- :contentReference[oaicite:4]{index=4} / :contentReference[oaicite:5]{index=5}
- HTML5 / CSS3
- [Bootstrap](https://getbootstrap.com/?utm_source=chatgpt.com)
- :contentReference[oaicite:7]{index=7} (optional)

## Planned Models

- User
- Category
- Video
- ChildProfile
- WatchHistory

## Example Use Case

A parent creates an account and adds categories such as:

- Cartoons
- Learning English
- Bedtime Stories
- Educational Videos

The parent then adds selected YouTube videos to each category. The child accesses the site and watches only the approved videos in a clean and distraction-free interface.

## Educational Purpose

This project is also intended as a practical learning exercise for web development with Django, covering:

- Django models and relationships
- Authentication and authorization
- Admin customization
- Template rendering
- Static and media files
- Docker deployment

## Future Enhancements

- Favorite videos
- Search functionality
- Viewing statistics
- Daily recommendations
- Parent dashboard
- REST API with [Django REST Framework](https://www.django-rest-framework.org/?utm_source=chatgpt.com)
- Mobile application integration

## License

This project is licensed under the MIT License.

## Author

Created as a family-focused educational project to provide children with a safer and more controlled online video experience.
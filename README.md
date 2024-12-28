Travel Agency Management System
Description: Developed a comprehensive Travel Agency Management System using Django, designed to streamline the operations of a travel agency. The system includes functionalities for managing clients, itineraries, hotels, activities, and transportation. It also features user authentication, availability verification, and PDF invoice generation.

Key Features:

Client Management: Allows the creation, modification, and deletion of client records. Clients can be searched and filtered by name.
Itinerary Planning: Facilitates the creation and finalization of travel itineraries for clients, including the management of daily activities and hotel bookings.
Hotel Management: Integrates with the Overpass API to fetch and display hotels in a specified geographic area. Users can search for hotels by name and view their availability.
Transportation Management: Manages different types of transportation options, including the ability to add, edit, and delete transport records.
Activity Management: Enables the addition and management of various activities that can be included in itineraries.
User Authentication: Implements user registration, login, and logout functionalities with Django's built-in authentication system.
PDF Invoice Generation: Generates detailed PDF invoices for finalized itineraries, including daily activities and total costs.
Dynamic Search and Pagination: Provides dynamic search and pagination for clients, itineraries, and transportation records to enhance user experience.
Technologies Used:

Backend: Django, Django REST Framework
Frontend: HTML, CSS, JavaScript
Database: SQLite (or any other database supported by Django)
APIs: Overpass API for fetching hotel data
Other Libraries: ReportLab for PDF generation
Responsibilities:

Designed and implemented the database schema and models for clients, itineraries, hotels, activities, and transportation.
Developed RESTful APIs using Django REST Framework for managing data.
Created dynamic and responsive frontend interfaces using HTML, CSS, and JavaScript.
Integrated third-party APIs to fetch and display hotel data.
Implemented user authentication and authorization to secure the application.
Developed custom views and templates to handle various user interactions and data presentations.
Ensured data integrity and consistency through form validations and error handling.
Generated PDF invoices for clients using ReportLab.

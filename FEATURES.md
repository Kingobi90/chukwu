# StudyMaster - Feature Overview

## 🎯 Core Features

### 1. **Campus Underground** 🏛️
- **Study Groups**: Join or create study groups for your courses
- **Study Buddies**: Connect with students in similar courses
- **Shared Resources**: Community-contributed study materials and notes
- **Quick Questions Board**: Ask and answer questions from peers

### 2. **Smart Study** 🧠
- **AI Flashcards**: Auto-generated flashcards from course materials
- **Spaced Repetition**: Intelligent review scheduling
- **Practice Quizzes**: AI-generated questions to test knowledge
- **Progress Tracking**: Visual progress indicators per course
- **Study Streaks**: Gamified learning with streak tracking
- **Custom Settings**: Adjustable difficulty and card count

### 3. **Live Class Sync** 📡
- **Real-time Moodle Integration**: Automatically syncs course materials
- **Auto-Processing**: Processes PDFs and creates study materials
- **Material Tracking**: Shows new, synced, and pending materials
- **Sync Settings**: Configurable auto-sync and notifications
- **Lecture Recordings**: Downloads and organizes recordings

### 4. **Focus Mode** 🎯
- **Pomodoro Timer**: Built-in timer with presets (25/50/15/5 minutes)
- **Distraction Blocking**: Optional distraction blocking
- **Session Tracking**: Logs all focus sessions
- **Ambient Sounds**: Optional background music
- **Statistics**: Daily, weekly, and lifetime stats
- **Visual Progress**: Circular progress indicator

### 5. **Accountability Circle** ⚡
- **Leaderboards**: Weekly rankings based on study performance
- **Study Challenges**: Compete in various challenges
- **Study Buddies**: Track friends' progress and updates
- **Achievements**: Unlock badges and milestones
- **Progress Sharing**: Share accomplishments with peers
- **Points System**: Earn points for study activities

### 6. **Brain Dump** ☁️
- **Quick Notes**: Capture thoughts instantly
- **Voice Memos**: Record audio notes with transcription
- **Tags & Filters**: Organize notes by tags and types
- **Search**: Fast search across all notes
- **Note Types**: Thoughts, Study Notes, Todos, Questions
- **Statistics**: Track note-taking habits

## 🔗 Integration Points

### Moodle Integration
- **Course Sync**: Automatically pulls courses and materials
- **File Access**: Direct access to course files and resources
- **Grade Tracking**: Monitors grades and generates AI insights
- **Calendar Events**: Syncs assignments and deadlines
- **Lecture Materials**: Organizes notes and recordings

### AI Features (OpenAI)
- **PDF Summarization**: Generates summaries of lecture PDFs
- **Flashcard Generation**: Creates flashcards from materials
- **Grade Analysis**: Provides insights and recommendations
- **Question Generation**: Creates practice questions
- **Voice Transcription**: Converts voice memos to text

## 🎨 Design Philosophy

- **Dark Theme**: Eye-friendly dark interface
- **Neon Accents**: Each feature has unique color scheme
  - Campus Underground: Green (#00ff88)
  - Smart Study: Teal (#4ecdc4)
  - Live Sync: Blue (#45b7d1)
  - Focus Mode: Orange (#f39c12)
  - Accountability: Red (#e74c3c)
  - Brain Dump: Purple (#9b59b6)

- **Animated UI**: Smooth transitions and hover effects
- **Responsive**: Works on desktop, tablet, and mobile
- **Glassmorphism**: Modern frosted glass effects

## 🚀 Getting Started

1. **Login**: Use your Moodle API token
2. **Explore Hub**: Navigate from the AI coach homepage
3. **Sync Courses**: Let Live Class Sync pull your materials
4. **Start Studying**: Use Smart Study for flashcards
5. **Track Progress**: Monitor in Accountability Circle
6. **Stay Focused**: Use Focus Mode for deep work
7. **Connect**: Join study groups in Campus Underground
8. **Capture Ideas**: Quick notes in Brain Dump

## 📊 Data Flow

```
Moodle API → Live Class Sync → Course Materials
                ↓
        Smart Study (AI Processing)
                ↓
        Flashcards + Quizzes
                ↓
        Progress Tracking
                ↓
        Accountability Circle
```

## 🔐 Privacy & Security

- **No passwords stored**: Uses API tokens only
- **Session-based**: Secure session management
- **Local processing**: Most data stays on your device
- **Encrypted storage**: SQLite databases for local data

## 🎯 Future Enhancements

- **Mobile App**: Native iOS/Android apps
- **Collaboration**: Real-time study sessions
- **Video Integration**: Lecture video analysis
- **Calendar Integration**: Google Calendar sync
- **Study Plans**: AI-generated study schedules
- **Peer Tutoring**: Built-in video chat for tutoring
- **Marketplace**: Buy/sell study materials
- **Course Reviews**: Rate and review courses

## 📱 URL Routes

- `/` - AI Coach Homepage
- `/campus-underground` - Study groups and community
- `/smart-study` - Flashcards and quizzes
- `/live-sync` - Moodle integration
- `/focus-mode` - Pomodoro timer
- `/accountability` - Leaderboards and challenges
- `/brain-dump` - Quick notes

## 🛠️ Tech Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML/CSS/JavaScript
- **AI**: OpenAI GPT-3.5
- **Database**: SQLite
- **API**: Moodle Web Services API
- **PDF Processing**: PyPDF2

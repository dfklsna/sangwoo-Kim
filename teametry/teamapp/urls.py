# teamapp/urls.py
from .views import test_connection
from django.urls import path
from .views import (
    TeamCreateView,
    RoomJoinView,
    ParticipantJoinView,
    SurveySubmitView,
    TeamAssignView,
    SurveyStatusView,
    TeamResultView,
    TeamDetailView,
    ParticipantSummaryView,
    TeamChangeView,
    TeamListView,
    RoomInfoView  
)

urlpatterns = [
    path('create_team/', TeamCreateView.as_view(), name='create_team'),
    path('join_room/', RoomJoinView.as_view(), name='join_room'),
    path('join_participant/', ParticipantJoinView.as_view(), name='join_participant'),
    path('submit_survey/', SurveySubmitView.as_view(), name='submit_survey'),
    path('team_assign/', TeamAssignView.as_view(), name='team_assign'),
    path('survey_status/', SurveyStatusView.as_view(), name='survey_status'),
    path('team_result/', TeamResultView.as_view(), name='team_result'),
    path('team_detail/<str:room_code>/<int:team_number>/', TeamDetailView.as_view(), name='team_detail'),
    path('participant_summary/<int:participant_id>/', ParticipantSummaryView.as_view(), name='participant_summary'),
    path('change_team_assignment/', TeamChangeView.as_view(), name='change_team_assignment'),
    path('api/team-list/', TeamListView.as_view()),
    path('rooms/<str:room_code>/info', RoomInfoView.as_view()),
    path("test/", test_connection),
]


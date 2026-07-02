import unittest
from unittest.mock import AsyncMock, patch, MagicMock
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext
from bot.handlers.start import cmd_start
from bot.handlers.gender import process_gender
from bot.states.user_states import AnalysisFlow

class TestHandlers(unittest.IsolatedAsyncioTestCase):

    @patch('bot.handlers.start.repository.upsert_user', new_callable=AsyncMock)
    async def test_cmd_start(self, mock_upsert_user):
        message = MagicMock(spec=Message)
        message.from_user.id = 123
        message.from_user.username = "test"
        message.from_user.first_name = "Test"
        message.answer_photo = AsyncMock()
        
        state = AsyncMock(spec=FSMContext)
        
        await cmd_start(message, state)
        
        mock_upsert_user.assert_called_once_with(123, "test", "Test")
        message.answer_photo.assert_called_once()
        state.set_state.assert_called_once_with(AnalysisFlow.waiting_for_photo)

    @patch('bot.handlers.gender.repository.get_user', new_callable=AsyncMock)
    @patch('bot.handlers.gender.repository.decrement_free_analysis', new_callable=AsyncMock)
    @patch('bot.handlers.gender.repository.create_analysis_job', new_callable=AsyncMock)
    @patch('bot.handlers.gender.queue_service.add_job', new_callable=AsyncMock)
    async def test_process_gender_free(self, mock_add_job, mock_create_job, mock_decrement, mock_get_user):
        callback = MagicMock(spec=CallbackQuery)
        callback.data = "gender:male"
        callback.from_user.id = 123
        callback.message.chat.id = 456
        callback.answer = AsyncMock()
        callback.message.edit_text = AsyncMock()
        
        mock_msg = MagicMock()
        mock_msg.message_id = 789
        callback.message.answer = AsyncMock(return_value=mock_msg)
        
        user_mock = MagicMock()
        user_mock.free_analyses = 1
        mock_get_user.return_value = user_mock
        
        job_mock = MagicMock()
        job_mock.id = 10
        mock_create_job.return_value = job_mock
        
        state = AsyncMock(spec=FSMContext)
        state.get_data = AsyncMock(return_value={"photo_path": "path.jpg"})
        
        await process_gender(callback, state)
        
        callback.answer.assert_called_once()
        state.update_data.assert_called_once_with(gender="male")
        mock_decrement.assert_called_once_with(123)
        state.set_state.assert_called_once_with(AnalysisFlow.processing)
        mock_add_job.assert_called_once()
        
if __name__ == '__main__':
    unittest.main()

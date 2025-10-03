import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { flashcardsAPI } from '@/lib/api'
import { ArrowLeft, RotateCcw, Check, X } from 'lucide-react'

export default function SmartStudy() {
  const [currentCardIndex, setCurrentCardIndex] = useState(0)
  const [showAnswer, setShowAnswer] = useState(false)
  const queryClient = useQueryClient()

  const { data: dueCards, isLoading } = useQuery({
    queryKey: ['dueFlashcards'],
    queryFn: async () => {
      const response = await flashcardsAPI.getDueFlashcards()
      return response.data
    },
  })

  const reviewMutation = useMutation({
    mutationFn: ({ cardId, quality }: { cardId: string; quality: number }) =>
      flashcardsAPI.reviewFlashcard(cardId, quality),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['dueFlashcards'] })
      setShowAnswer(false)
      setCurrentCardIndex((prev) => prev + 1)
    },
  })

  const currentCard = dueCards?.[currentCardIndex]

  const handleReview = (quality: number) => {
    if (currentCard) {
      reviewMutation.mutate({ cardId: currentCard.id, quality })
    }
  }

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-teal-900 to-gray-900 flex items-center justify-center">
        <div className="text-white text-xl">Loading flashcards...</div>
      </div>
    )
  }

  if (!dueCards || dueCards.length === 0 || currentCardIndex >= dueCards.length) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-teal-900 to-gray-900">
        <div className="max-w-4xl mx-auto px-4 py-8">
          <Link to="/" className="inline-flex items-center text-teal-400 hover:text-teal-300 mb-8">
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Dashboard
          </Link>
          
          <div className="glass p-12 rounded-2xl text-center">
            <div className="text-6xl mb-4">🎉</div>
            <h2 className="text-3xl font-bold text-white mb-4">All Caught Up!</h2>
            <p className="text-gray-400 mb-8">
              You've reviewed all your due flashcards. Great job!
            </p>
            <Link
              to="/"
              className="inline-block px-6 py-3 bg-gradient-to-r from-teal-600 to-cyan-600 hover:from-teal-700 hover:to-cyan-700 text-white font-semibold rounded-lg transition-all"
            >
              Return to Dashboard
            </Link>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-teal-900 to-gray-900">
      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="flex items-center justify-between mb-8">
          <Link to="/" className="inline-flex items-center text-teal-400 hover:text-teal-300">
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Dashboard
          </Link>
          
          <div className="text-white">
            Card {currentCardIndex + 1} of {dueCards.length}
          </div>
        </div>

        {/* Flashcard */}
        <div className="glass p-12 rounded-2xl mb-8 min-h-[400px] flex flex-col items-center justify-center">
          <div className="text-center w-full">
            <p className="text-sm text-gray-400 mb-4">
              {showAnswer ? 'Answer' : 'Question'}
            </p>
            <div className="text-2xl text-white mb-8 whitespace-pre-wrap">
              {showAnswer ? currentCard.back : currentCard.front}
            </div>
          </div>

          {!showAnswer && (
            <button
              onClick={() => setShowAnswer(true)}
              className="px-8 py-3 bg-gradient-to-r from-teal-600 to-cyan-600 hover:from-teal-700 hover:to-cyan-700 text-white font-semibold rounded-lg transition-all"
            >
              Show Answer
            </button>
          )}
        </div>

        {/* Review Buttons */}
        {showAnswer && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <button
              onClick={() => handleReview(0)}
              className="p-4 glass hover:bg-red-500/20 rounded-xl transition-colors"
            >
              <X className="w-6 h-6 text-red-400 mx-auto mb-2" />
              <p className="text-sm text-white">Again</p>
              <p className="text-xs text-gray-400">{'<1m'}</p>
            </button>
            
            <button
              onClick={() => handleReview(2)}
              className="p-4 glass hover:bg-orange-500/20 rounded-xl transition-colors"
            >
              <RotateCcw className="w-6 h-6 text-orange-400 mx-auto mb-2" />
              <p className="text-sm text-white">Hard</p>
              <p className="text-xs text-gray-400">{'<10m'}</p>
            </button>
            
            <button
              onClick={() => handleReview(3)}
              className="p-4 glass hover:bg-blue-500/20 rounded-xl transition-colors"
            >
              <Check className="w-6 h-6 text-blue-400 mx-auto mb-2" />
              <p className="text-sm text-white">Good</p>
              <p className="text-xs text-gray-400">1d</p>
            </button>
            
            <button
              onClick={() => handleReview(5)}
              className="p-4 glass hover:bg-green-500/20 rounded-xl transition-colors"
            >
              <Check className="w-6 h-6 text-green-400 mx-auto mb-2" />
              <p className="text-sm text-white">Easy</p>
              <p className="text-xs text-gray-400">4d</p>
            </button>
          </div>
        )}
      </div>
    </div>
  )
}

import { Box, Image, Text, Spinner, Center } from '@chakra-ui/react'
import { useState, useEffect } from 'react'
import axios from 'axios'
import { useVisualization } from '../contexts/VisualizationContext'

export const Visualization = () => {
  const { visualizationUrl, visualizationType } = useVisualization()
  const [imageUrl, setImageUrl] = useState<string>('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    // If we have a visualization URL from the context, use it
    if (visualizationUrl) {
      // If the URL is already a blob URL, use it directly
      if (visualizationUrl.startsWith('blob:')) {
        setImageUrl(visualizationUrl)
      } else {
        // Otherwise, load it from the API
        loadImageFromApi(visualizationUrl)
      }
    }
  }, [visualizationUrl])

  const loadImageFromApi = async (apiUrl: string) => {
    try {
      setLoading(true)
      setError('')
      console.log(`Loading image from API URL: ${apiUrl}`)
      
      // Load the image from the API
      const response = await axios.get(`http://localhost:8000${apiUrl}`, {
        responseType: 'blob'
      })
      
      const url = URL.createObjectURL(response.data)
      setImageUrl(url)
    } catch (error) {
      console.error('Error loading image:', error)
      setError('Error loading visualization')
    } finally {
      setLoading(false)
    }
  }

  const loadVisualization = async (bandName: string) => {
    try {
      setLoading(true)
      setError('')
      const response = await axios.get(`http://localhost:8000/api/visualize/${bandName}`, {
        responseType: 'blob'
      })
      const url = URL.createObjectURL(response.data)
      setImageUrl(url)
    } catch (error) {
      setError('Error loading visualization')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Box bg="blue.800" p={6} borderRadius="lg" w="100%" minH="500px">
      <Text fontSize="xl" fontWeight="bold" mb={4}>
        Visualization {visualizationType !== 'none' && `(${visualizationType})`}
      </Text>
      {loading ? (
        <Center h="400px">
          <Spinner size="xl" />
        </Center>
      ) : error ? (
        <Center h="400px">
          <Text color="red.300">{error}</Text>
        </Center>
      ) : imageUrl ? (
        <Image
          src={imageUrl}
          alt="Visualization"
          w="100%"
          h="400px"
          objectFit="contain"
          borderRadius="md"
        />
      ) : (
        <Center h="400px">
          <Text color="gray.400">Select a band or perform a calculation to visualize</Text>
        </Center>
      )}
    </Box>
  )
} 
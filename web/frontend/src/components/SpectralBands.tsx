import { Box, Text, Button, useToast, VStack } from '@chakra-ui/react'
import { useState, useEffect } from 'react'
import axios from 'axios'
import { useVisualization } from '../contexts/VisualizationContext'

interface BandInfo {
  description: string
  wavelength: string
  dimensions: string
}

export const SpectralBands = () => {
  const [bands, setBands] = useState<Record<string, BandInfo>>({})
  const [selectedBand, setSelectedBand] = useState<string>('')
  const toast = useToast()
  const { setVisualizationUrl, setVisualizationType, setSelectedBand: setContextBand } = useVisualization()

  useEffect(() => {
    const fetchBands = async () => {
      try {
        const response = await axios.get('http://localhost:8000/api/bands')
        setBands(response.data.data)
      } catch (error) {
        toast({
          title: 'Error fetching bands',
          status: 'error',
          duration: 3000,
          isClosable: true,
        })
      }
    }
    fetchBands()
  }, [toast])

  const handleBandSelect = async (bandName: string) => {
    try {
      setSelectedBand(bandName)
      setContextBand(bandName)
      
      // Convert the band to COG format
      await axios.post(`http://localhost:8000/api/convert/${bandName}`)
      
      // Load the visualization for this band
      try {
        setVisualizationType('band')
        setVisualizationUrl(`/api/visualize/${bandName}`)
      } catch (visualizationError) {
        console.error('Error setting visualization:', visualizationError)
      }
      
      toast({
        title: 'Band converted successfully',
        status: 'success',
        duration: 2000,
        isClosable: true,
      })
    } catch (error) {
      toast({
        title: 'Error converting band',
        status: 'error',
        duration: 3000,
        isClosable: true,
      })
    }
  }

  return (
    <Box bg="blue.800" p={6} borderRadius="lg" w="100%">
      <Text fontSize="xl" fontWeight="bold" mb={4}>
        Spectral Bands
      </Text>
      <VStack spacing={3} align="stretch">
        {Object.entries(bands).map(([name, info]) => (
          <Button
            key={name}
            onClick={() => handleBandSelect(name)}
            colorScheme={selectedBand === name ? 'green' : 'blue'}
            variant={selectedBand === name ? 'solid' : 'outline'}
            size="lg"
            justifyContent="flex-start"
            whiteSpace="normal"
            textAlign="left"
            h="auto"
            py={4}
          >
            <VStack align="flex-start" spacing={1}>
              <Text fontWeight="bold">{info.description}</Text>
              <Text fontSize="sm" opacity={0.8}>
                {info.wavelength} | {info.dimensions}
              </Text>
            </VStack>
          </Button>
        ))}
      </VStack>
    </Box>
  )
} 
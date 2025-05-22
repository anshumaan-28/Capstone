import { Box, Text, SimpleGrid, Stat, StatLabel, StatNumber, Spinner, Center } from '@chakra-ui/react'
import { useState, useEffect } from 'react'
import axios from 'axios'
import { useVisualization } from '../contexts/VisualizationContext'

interface BandStats {
  minimum: number
  maximum: number
  mean: number
  std: number
}

export const DataStatistics = () => {
  const { selectedBand } = useVisualization()
  const [stats, setStats] = useState<BandStats | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    if (selectedBand) {
      loadStatistics(selectedBand)
    }
  }, [selectedBand])

  const loadStatistics = async (bandName: string) => {
    try {
      setLoading(true)
      setError('')
      console.log(`Loading statistics for band: ${bandName}`)
      const response = await axios.get(`http://localhost:8000/api/statistics/${bandName}`)
      
      if (response.data && response.data.data) {
        setStats(response.data.data)
      } else {
        setError('Statistics data format is invalid')
      }
    } catch (error) {
      console.error('Error loading statistics:', error)
      setError('Failed to load statistics')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Box bg="blue.800" p={6} borderRadius="lg" w="100%">
      <Text fontSize="xl" fontWeight="bold" mb={4}>
        Data Statistics {selectedBand ? `(${selectedBand})` : ''}
      </Text>
      
      {loading ? (
        <Center h="100px">
          <Spinner size="md" />
        </Center>
      ) : error ? (
        <Text color="red.300">{error}</Text>
      ) : stats ? (
        <SimpleGrid columns={{ base: 2, md: 4 }} spacing={4}>
          <Stat>
            <StatLabel>Minimum</StatLabel>
            <StatNumber>{stats.minimum.toFixed(2)}</StatNumber>
          </Stat>
          <Stat>
            <StatLabel>Maximum</StatLabel>
            <StatNumber>{stats.maximum.toFixed(2)}</StatNumber>
          </Stat>
          <Stat>
            <StatLabel>Mean</StatLabel>
            <StatNumber>{stats.mean.toFixed(2)}</StatNumber>
          </Stat>
          <Stat>
            <StatLabel>Std. Deviation</StatLabel>
            <StatNumber>{stats.std.toFixed(2)}</StatNumber>
          </Stat>
        </SimpleGrid>
      ) : (
        <Text color="gray.400">Select a band to view statistics</Text>
      )}
    </Box>
  )
} 
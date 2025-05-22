import {
  Box,
  Text,
  Select,
  Button,
  VStack,
  HStack,
  useToast
} from '@chakra-ui/react'
import { useState } from 'react'
import axios from 'axios'
import { useVisualization } from '../contexts/VisualizationContext'

export const BandManipulations = () => {
  const [operation, setOperation] = useState('ratio')
  const [band1, setBand1] = useState('')
  const [band2, setBand2] = useState('')
  const [loading, setLoading] = useState(false)
  const toast = useToast()
  const { setVisualizationUrl, setVisualizationType } = useVisualization()

  const handleCalculate = async () => {
    if (!band1 || !band2) {
      toast({
        title: 'Please select both bands',
        status: 'warning',
        duration: 3000,
        isClosable: true,
      })
      return
    }

    setLoading(true)
    try {
      // First ensure both bands are converted to COG format
      console.log(`Converting band 1: ${band1}`)
      await axios.post(`http://localhost:8000/api/convert/${band1}`)
      
      console.log(`Converting band 2: ${band2}`)
      await axios.post(`http://localhost:8000/api/convert/${band2}`)
      
      // Confirm both bands exist as COG files
      console.log("Checking available COGs...")
      const cogsResponse = await axios.get(`http://localhost:8000/api/bands`)
      console.log("Available bands:", cogsResponse.data)
      
      const endpoint = operation === 'ratio' 
        ? '/api/manipulate/ratio'
        : '/api/manipulate/difference'

      const payload = operation === 'ratio'
        ? { numerator: band1, denominator: band2 }
        : { band1, band2 }

      console.log("Submitting manipulation request:", { endpoint, payload })
      const response = await axios.post(`http://localhost:8000${endpoint}`, payload)
      console.log("Manipulation response:", response.data)
      
      if (response.data && response.data.status === 'success') {
        // Load the visualization image
        const visualizationPath = response.data.data.visualization
        console.log("Visualization path:", visualizationPath)
        
        // Update the visualization context
        setVisualizationUrl(visualizationPath)
        setVisualizationType('manipulation')
        
        toast({
          title: 'Calculation completed',
          status: 'success',
          duration: 2000,
          isClosable: true,
        })
      } else {
        throw new Error("Manipulation completed but response format is unexpected")
      }
    } catch (error: any) {
      console.error("Error in band manipulation:", error)
      toast({
        title: 'Error performing calculation',
        description: error.response?.data?.detail || error.message,
        status: 'error',
        duration: 3000,
        isClosable: true,
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <Box bg="blue.800" p={6} borderRadius="lg" w="100%">
      <Text fontSize="xl" fontWeight="bold" mb={4}>
        Band Manipulations
      </Text>
      <VStack spacing={4} align="stretch">
        <Select
          value={operation}
          onChange={(e) => setOperation(e.target.value)}
          bg="blue.700"
          color="white"
        >
          <option value="ratio">Band Ratio</option>
          <option value="difference">Band Difference</option>
        </Select>
        
        <HStack spacing={4}>
          <Select
            placeholder="Select first band"
            value={band1}
            onChange={(e) => setBand1(e.target.value)}
            bg="blue.700"
            color="white"
          >
            <option value="IMG_VIS">Visible</option>
            <option value="IMG_SWIR">Short Wave IR</option>
            <option value="IMG_MIR">Middle IR</option>
            <option value="IMG_WV">Water Vapor</option>
            <option value="IMG_TIR1">Thermal IR1</option>
            <option value="IMG_TIR2">Thermal IR2</option>
          </Select>
          
          <Select
            placeholder="Select second band"
            value={band2}
            onChange={(e) => setBand2(e.target.value)}
            bg="blue.700"
            color="white"
          >
            <option value="IMG_VIS">Visible</option>
            <option value="IMG_SWIR">Short Wave IR</option>
            <option value="IMG_MIR">Middle IR</option>
            <option value="IMG_WV">Water Vapor</option>
            <option value="IMG_TIR1">Thermal IR1</option>
            <option value="IMG_TIR2">Thermal IR2</option>
          </Select>
        </HStack>
        
        <Button
          colorScheme="green"
          onClick={handleCalculate}
          isLoading={loading}
        >
          Calculate {operation === 'ratio' ? 'Ratio' : 'Difference'}
        </Button>
      </VStack>
    </Box>
  )
} 
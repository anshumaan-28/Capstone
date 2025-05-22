import { Box, Heading, Text } from '@chakra-ui/react'
import { FaSatellite } from 'react-icons/fa'

export const Header = () => {
  return (
    <Box bg="blue.900" p={6} textAlign="center">
      <Heading size="xl" display="flex" alignItems="center" justifyContent="center" gap={4}>
        <FaSatellite /> INSAT COG Data Explorer
      </Heading>
      <Text mt={2} fontSize="lg">
        Visualization and Manipulation of Satellite Spectral Bands
      </Text>
    </Box>
  )
} 
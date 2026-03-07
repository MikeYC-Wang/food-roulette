import { ref } from 'vue';

// 定義位置型別
interface UserLocation {
  lat: number;
  lng: number;
  status: 'loading' | 'success' | 'error' | 'default';
  message: string;
}

export function useLocation() {
  // 預設值：基隆市安樂區
  const DEFAULT_LAT = 25.1215;
  const DEFAULT_LNG = 121.7195;

  const location = ref<UserLocation>({
    lat: DEFAULT_LAT,
    lng: DEFAULT_LNG,
    status: 'loading',
    message: '正在獲取定位...',
  });

  const getLocation = () => {
    if (!navigator.geolocation) {
      location.value.status = 'default';
      location.value.message = '瀏覽器不支援定位，使用預設位置';
      return;
    }

    const options = {
      enableHighAccuracy: true,
      timeout: 5000,
      maximumAge: 0,
    };

    navigator.geolocation.getCurrentPosition(
      (position) => {
        location.value = {
          lat: position.coords.latitude,
          lng: position.coords.longitude,
          status: 'success',
          message: '定位成功',
        };
      },
      (error) => {
        console.warn('定位失敗:', error.message);
        location.value.status = 'default';
        location.value.message = '無法取得定位，使用預設位置(基隆)';
      },
      options
    );
  };

  return {
    location,
    getLocation,
  };
}
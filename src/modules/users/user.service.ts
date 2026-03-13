// A simple mocked user service returning dummy tokens

export interface User {
  id: string;
  name: string;
}

export class UserService {
  async authenticateUser(token: string): Promise<User | null> {
    // In a real app we would decode/verify the JWT here
    if (token === 'mock-token') {
      return { id: 'user-123', name: 'Alice' };
    }
    return null;
  }
}

export const userService = new UserService();
